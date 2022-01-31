import calendar
import datetime
import os
from typing import Union

import mysql.connector
from flask import render_template, session, redirect, url_for, Response, request


class Index:

    def __init__(self):
        self.__db = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT', 3306),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_DATABASE'),
        )

    def show(self) -> Union[str, Response]:
        if 'character_id' not in session:
            return redirect(url_for('auth_login'))

        # request params
        current_year = datetime.datetime.now().year
        query_params = {
            'mode': request.args.get('mode', 'details'),
            'corporation': self.__int(request.args.get('corporation', 0)),
            'year': self.__int(request.args.get('year', current_year)),
            'month': self.__int(request.args.get('month', datetime.datetime.now().month)),
            'type_bounty': request.args.get('type_bounty', '0'),
            'type_ess_escrow': request.args.get('type_ess_escrow', '0'),
            'type_mission_reward': request.args.get('type_mission_reward', '0'),
            'type_corporate_reward': request.args.get('type_corporate_reward', '0'),
            'type_brokers_fee': request.args.get('type_brokers_fee', '0'),
            'type_jump_clone': request.args.get('type_jump_clone', '0'),
            'type_reprocessing': request.args.get('type_reprocessing', '0'),
            'type_industry_job': request.args.get('type_industry_job', '0'),
            'type_planetary': request.args.get('type_planetary', '0'),
            'type_office_rental': request.args.get('type_office_rental', '0'),
            'type_project_discovery': request.args.get('type_project_discovery', '0'),
        }

        # ref types
        types = []
        types_placeholder = []
        if query_params['type_bounty'] == '1':
            types.append('bounty_prizes')
            types_placeholder.append('%s')
        if query_params['type_ess_escrow'] == '1':
            types.append('ess_escrow_transfer')
            types_placeholder.append('%s')
        if query_params['type_mission_reward'] == '1':
            types.append('agent_mission_reward')
            types.append('agent_mission_time_bonus_reward')
            types_placeholder.append('%s')
            types_placeholder.append('%s')
        if query_params['type_corporate_reward'] == '1':
            types.append('corporate_reward_payout')
            types_placeholder.append('%s')
        if query_params['type_brokers_fee'] == '1':
            types.append('brokers_fee')
            types_placeholder.append('%s')
        if query_params['type_jump_clone'] == '1':
            types.append('jump_clone_activation_fee')
            types.append('jump_clone_installation_fee')
            types_placeholder.append('%s')
            types_placeholder.append('%s')
        if query_params['type_reprocessing'] == '1':
            types.append('reprocessing_tax')
            types_placeholder.append('%s')
        if query_params['type_industry_job'] == '1':
            types.append('industry_job_tax')
            types_placeholder.append('%s')
        if query_params['type_planetary'] == '1':
            types.append('planetary_export_tax')
            types.append('planetary_import_tax')
            types_placeholder.append('%s')
            types_placeholder.append('%s')
        if query_params['type_office_rental'] == '1':
            types.append('office_rental_fee')
            types_placeholder.append('%s')
        if query_params['type_project_discovery'] == '1':
            types.append('project_discovery_reward')
            types_placeholder.append('%s')

        # journal date range
        date_from = datetime.datetime(query_params['year'], query_params['month'], 1)
        weekday, last_day = calendar.monthrange(query_params['year'], query_params['month'])
        date_to = datetime.datetime(query_params['year'], query_params['month'], last_day, 23, 59, 59)

        journal = []
        if query_params['mode'] == 'details':
            journal = self.__fetch_details(query_params['corporation'], date_from, date_to, types, types_placeholder)
        elif query_params['mode'] == 'sum_month':
            journal = self.__fetch_sum_month(query_params['corporation'], types, types_placeholder)
        elif query_params['mode'] == 'sum_corporation':
            journal = self.__fetch_sum_corporation(date_from, date_to, types, types_placeholder)

        sum_amount = 0
        for entry in journal:
            sum_amount += entry['amount']

        # fetch corporations
        cursor = self.__db.cursor(dictionary=True)
        cursor.execute("SELECT id, corporation_name, last_journal_date FROM corporations "
                       "WHERE active = 1 ORDER BY corporation_name")
        corporations = cursor.fetchall()
        cursor.close()

        self.__db.close()

        return render_template('index.html', character_id=session['character_id'], current_year=current_year,
                               params=query_params, corporations=corporations, journal=journal, sum_amount=sum_amount)

    def __fetch_details(self, corporation: int, date_from: datetime, date_to: datetime, types: [],
                        types_placeholder: []) -> []:
        journal = []
        if len(types) > 0:
            cursor = self.__db.cursor(dictionary=True)
            cursor.execute("SELECT ref_type, journal_date, description, amount, reason "
                           "FROM wallet_journal "
                           "WHERE corporation_id = %s AND journal_date BETWEEN %s AND %s AND ref_type IN ({}) "
                           "ORDER BY journal_date DESC".format(', '.join(types_placeholder)),
                           [corporation, date_from.strftime('%Y-%m-%d %H:%M:%S'),
                            date_to.strftime('%Y-%m-%d %H:%M:%S')] + types)
            journal = cursor.fetchall()
            cursor.close()
        return journal

    def __fetch_sum_month(self, corporation: int, types: [], types_placeholder: []) -> []:
        journal = []
        if len(types) > 0:
            cursor = self.__db.cursor(dictionary=True)
            cursor.execute("SELECT SUM(amount) AS amount, YEAR(journal_date) AS year, MONTH(journal_date) AS month "
                           "FROM wallet_journal "
                           "WHERE corporation_id = %s AND ref_type IN ({}) "
                           "GROUP BY YEAR(journal_date), MONTH(journal_date)"
                           "ORDER BY YEAR(journal_date) DESC, MONTH(journal_date) DESC"
                           .format(', '.join(types_placeholder)),
                           [corporation] + types)
            journal = cursor.fetchall()
            cursor.close()
        return journal

    def __fetch_sum_corporation(self, date_from: datetime, date_to: datetime, types: [], types_placeholder: []) -> []:
        journal = []
        if len(types) > 0:
            cursor = self.__db.cursor(dictionary=True)
            cursor.execute("SELECT w.corporation_id, SUM(w.amount) as amount, c.corporation_name "
                           "FROM wallet_journal w "
                           "LEFT JOIN corporations c ON w.corporation_id = c.id "
                           "WHERE w.journal_date BETWEEN %s AND %s AND w.ref_type IN ({}) "
                           "GROUP BY w.corporation_id, c.corporation_name "
                           "ORDER BY c.corporation_name".format(', '.join(types_placeholder)),
                           [date_from.strftime('%Y-%m-%d %H:%M:%S'), date_to.strftime('%Y-%m-%d %H:%M:%S')] + types)
            journal = cursor.fetchall()
            cursor.close()
        return journal

    @staticmethod
    def __int(s) -> int:
        try:
            integer = int(s)
            return integer
        except (ValueError, TypeError):
            return 0
