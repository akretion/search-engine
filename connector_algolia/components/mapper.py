# Copyright 2021 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.component.core import Component


class AlgoliaJsonExportMapper(Component):
    _name = "algolia.json.export.mapper"
    _inherit = ["json.export.mapper", "algolia.se.connector"]

    def _apply(self, map_record, options=None):
        res = super()._apply(map_record, options=None)
        # Algolia do not use the key "id" as key for the record but use "objectID"
        # By default we set this key to the value of the id
        # in case that you need something different you can customize your exporter
        if "objectID" not in res:
            res["objectID"] = res["id"]
        return res
