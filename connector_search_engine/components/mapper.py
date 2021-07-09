# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.component.core import Component


class JsonExportMapper(Component):
    _name = "json.export.mapper"
    _inherit = ["base.se.connector", "base.export.mapper"]
    _usage = "se.export.mapper"

    def __init__(self, work):
        """
        :param work: current environment (backend, session, ...)
        :type connector_env: :py:class:`connector.connector.Environment`
        """
        super(JsonExportMapper, self).__init__(work)
        exporter = work.index.exporter_id
        self._json_parser = exporter.get_json_parser()
        mapping_id = [
            mapping
            for mapping in self._json_parser["fields"]
            if isinstance(mapping, dict)
            and (mapping["name"] == "id" or mapping.get("target") == "id")
        ]
        if not mapping_id:
            self._json_parser["fields"].append(
                {"name": "record_id", "target": "id", "function": "_jsonify_m2o_to_id"}
            )

    def _apply(self, map_record, options=None):
        return map_record._source.jsonify(self._json_parser)[0]
