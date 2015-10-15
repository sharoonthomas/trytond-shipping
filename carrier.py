# -*- coding: utf-8 -*-
"""
    carrier.py

"""
from trytond.pool import PoolMeta, Pool
from trytond.model import fields
from trytond.transaction import Transaction

__all__ = ['Carrier']
__metaclass__ = PoolMeta


class Carrier:
    "Carrier"
    __name__ = 'carrier'

    currency = fields.Many2One('currency.currency', 'Currency', required=True)
    services = fields.One2Many(
        'carrier.service', 'carrier', 'Services', context={'active': False}
    )

    @staticmethod
    def default_currency():
        Company = Pool().get('company.company')

        company = Transaction().context.get('company')
        if company:
            return Company(company).currency.id

    def get_all_services(self):
        """
        Return a list of services handled by the carrier

        Downstream modules should implement this method to return a list of
        services of the carrier.
        """
        return []

    @fields.depends(['services', 'carrier_cost_method'])
    def on_change_carrier_cost_method(self):
        """
        On change of a carrier cost method return the list of carriers
        on_change.
        """
        if self.services:
            # if services are already defined, dont bother
            return

        changes = {
            'services': {
                'add': [],
            }
        }

        for service in self.get_all_services():
            changes['services']['add'].append((-1, service))

        return changes

    def get_rates(self):
        """
        Expects a list of tuples as:
            [
                (
                    <display method name>, <rate>, <currency>, <metadata>,
                    <write_vals>
                )
                ...
            ]

        Downstream shipping modules can implement this to get shipping rates.
        """
        # TODO: Remove this method in next version and use `get_shipping_rates`
        # method in sale instead
        return []  # pragma: no cover


class Service(ModelSQL, ModelView):
    "Carrier Services"
    __name__ = 'carrier.service'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    carrier = fields.Many2One('carrier', 'Carrier', required=True, select=True)
    active = fields.Boolean('Active', select=True)
    domestic = fields.Boolean('Domestic', select=True)
    international = fields.Boolean('International', select=True)
