# Copyright 2013 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.addons.queue_job.job import job


class SeBinding(models.AbstractModel):
    _name = 'se.binding'
    _se_model = True

    se_backend_id = fields.Many2one(
        'se.backend',
        related="index_id.backend_id")
    index_id = fields.Many2one(
        'se.index',
        string="Index",
        required=True,
        # TODO: shall we use 'restrict' here to preserve existing data?
        ondelete='cascade'
    )
    sync_state = fields.Selection([
        ('new', 'New'),
        ('to_update', 'To update'),
        ('scheduled', 'Scheduled'),
        ('done', 'Done'),
    ],
        default='new',
        readonly=True)
    date_modified = fields.Date(readonly=True)
    date_syncronized = fields.Date(readonly=True)
    data = fields.Serialized()

    def get_export_data(self):
        """Public method to retrieve export data."""
        return self.data

    @api.model
    def create(self, vals):
        record = super(SeBinding, self).create(vals)
        record._jobify_recompute_json()
        return record

    def _jobify_recompute_json(self, force_export=False):
        description = _('Recompute %s json and check if need update'
                        % self._name)
        for record in self:
            record.with_delay(description=description).recompute_json(
                force_export=force_export)

    def _work_by_index(self):
        for backend in self.mapped('se_backend_id'):
            for index in self.mapped('index_id'):
                bindings = self.filtered(
                    lambda b, backend=backend, index=index:
                    b.se_backend_id == backend and b.index_id == index)
                specific_backend = backend.specific_backend
                with specific_backend.work_on(
                    self._name, records=bindings, index=index
                ) as work:
                    yield work

    # TODO maybe we need to add lock (todo check)
    @job(default_channel='root.search_engine.recompute_json')
    def recompute_json(self, force_export=False):
        for work in self._work_by_index():
            mapper = work.component(usage='se.export.mapper')
            lang = work.index.lang_id.code
            for record in work.records.with_context(lang=lang):
                data = mapper.map_record(record).values()
                if record.data != data or force_export:
                    vals = {'data': data}
                    if record.sync_state in ('done', 'new'):
                        vals['sync_state'] = 'to_update'
                    record.write(vals)

    @job(default_channel='root.search_engine')
    @api.multi
    def export(self):
        for work in self._work_by_index():
            exporter = work.component(usage='se.record.exporter')
            exporter.run()

    @job(default_channel='root.search_engine')
    @api.multi
    def unsynchronize(self):
        """
        Unsynchronize/delete current recordset from backend
        :return: bool
        """
        for index in self.mapped('index_id'):
            # Same index means: same backend and same lang
            bindings = self.filtered(lambda r, i=index: r.index_id == i)
            specific_backend = index.se_backend_id.specific_backend
            with specific_backend.work_on(
                    self._name, records=bindings, index=index) as work:
                deleter = work.component(usage='record.exporter.deleter')
                deleter.run()
        return True
