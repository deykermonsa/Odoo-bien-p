# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re
import textwrap
from binascii import Error as binascii_error
from collections import defaultdict

from odoo import _, api, Command, fields, models, modules, tools
from odoo.exceptions import AccessError
from odoo.osv import expression
from odoo.tools import clean_context, groupby as tools_groupby, SQL

_logger = logging.getLogger(__name__)
_image_dataurl = re.compile(r'(data:image/[a-z]+?);base64,([a-z0-9+/\n]{3,}=*)\n*([\'"])(?: data-filename="([^"]*)")?', re.I)


class Message(models.Model):
    """ Message model (from notifications to user input).

    Note:: State management / Error codes / Failure types summary

    * mail.notification
      * notification_status
        'ready', 'sent', 'bounce', 'exception', 'canceled'
      * notification_type
        'inbox', 'email', 'sms' (SMS addon), 'snail' (snailmail addon)
      * failure_type
        # generic
        unknown,
        # mail
        "mail_email_invalid", "mail_smtp", "mail_email_missing",
        "mail_from_invalid", "mail_from_missing",
        # sms (SMS addon)
        'sms_number_missing', 'sms_number_format', 'sms_credit',
        'sms_server', 'sms_acc'
        # snailmail (snailmail addon)
        'sn_credit', 'sn_trial', 'sn_price', 'sn_fields',
        'sn_format', 'sn_error'

    * mail.mail
      * state
        'outgoing', 'sent', 'received', 'exception', 'cancel'
      * failure_reason: text

    * sms.sms (SMS addon)
      * state
        'outgoing', 'sent', 'error', 'canceled'
      * error_code
        'sms_number_missing', 'sms_number_format', 'sms_credit',
        'sms_server', 'sms_acc',
        # mass mode specific codes
        'sms_blacklist', 'sms_duplicate'

    * snailmail.letter (snailmail addon)
      * state
        'pending', 'sent', 'error', 'canceled'
      * error_code
        'CREDIT_ERROR', 'TRIAL_ERROR', 'NO_PRICE_AVAILABLE', 'FORMAT_ERROR',
        'UNKNOWN_ERROR',

    See ``mailing.trace`` model in mass_mailing application for mailing trace
    information.
    """
    _name = 'mail.message'
    _description = 'Message'
    _order = 'id desc'
    _rec_name = 'record_name'

    @api.model
    def default_get(self, fields):
        res = super(Message, self).default_get(fields)
        missing_author = 'author_id' in fields and 'author_id' not in res
        missing_email_from = 'email_from' in fields and 'email_from' not in res
        if missing_author or missing_email_from:
            author_id, email_from = self.env['mail.thread']._message_compute_author(res.get('author_id'), res.get('email_from'), raise_on_email=False)
            if missing_email_from:
                res['email_from'] = email_from
            if missing_author:
                res['author_id'] = author_id
        return res

    # content
    subject = fields.Char('Subject')
    date = fields.Datetime('Date', default=fields.Datetime.now)
    body = fields.Html('Contents', default='', sanitize_style=True)
    description = fields.Char(
        'Short description', compute="_compute_description",
        help='Message description: either the subject, or the beginning of the body')
    preview = fields.Char(
        'Preview', compute='_compute_preview',
        help='The text-only beginning of the body used as email preview.')
    link_preview_ids = fields.One2many(
        'mail.link.preview', 'message_id', string='Link Previews',
        groups="base.group_erp_manager")
    reaction_ids = fields.One2many(
        'mail.message.reaction', 'message_id', string="Reactions",
        groups="base.group_system")
    # Attachments are linked to a document through model / res_id and to the message through this field.
    attachment_ids = fields.Many2many(
        'ir.attachment', 'message_attachment_rel',
        'message_id', 'attachment_id',
        string='Attachments')
    parent_id = fields.Many2one(
        'mail.message', 'Parent Message', index='btree_not_null', ondelete='set null')
    child_ids = fields.One2many('mail.message', 'parent_id', 'Child Messages')
    # related document
    model = fields.Char('Related Document Model')
    res_id = fields.Many2oneReference('Related Document ID', model_field='model')
    record_name = fields.Char('Message Record Name') # display_name of the related document
    record_alias_domain_id = fields.Many2one('mail.alias.domain', 'Alias Domain', ondelete='set null')
    record_company_id = fields.Many2one('res.company', 'Company', ondelete='set null')
    # characteristics
    message_type = fields.Selection([
        ('email', 'Incoming Email'),
        ('comment', 'Comment'),
        ('email_outgoing', 'Outgoing Email'),
        ('notification', 'System notification'),
        ('auto_comment', 'Automated Targeted Notification'),
        ('user_notification', 'User Specific Notification')],
        'Type', required=True, default='comment',
        help="Used to categorize message generator"
             "\n'email': generated by an incoming email e.g. mailgateway"
             "\n'comment': generated by user input e.g. through discuss or composer"
             "\n'email_outgoing': generated by a mailing"
             "\n'notification': generated by system e.g. tracking messages"
             "\n'auto_comment': generated by automated notification mechanism e.g. acknowledgment"
             "\n'user_notification': generated for a specific recipient"
        )
    subtype_id = fields.Many2one('mail.message.subtype', 'Subtype', ondelete='set null', index=True)
    mail_activity_type_id = fields.Many2one(
        'mail.activity.type', 'Mail Activity Type',
        index='btree_not_null', ondelete='set null')
    is_internal = fields.Boolean('Employee Only', help='Hide to public / portal users, independently from subtype configuration.')
    # origin
    email_from = fields.Char('From', help="Email address of the sender. This field is set when no matching partner is found and replaces the author_id field in the chatter.")
    author_id = fields.Many2one(
        'res.partner', 'Author', index=True, ondelete='set null',
        help="Author of the message. If not set, email_from may hold an email address that did not match any partner.")
    author_avatar = fields.Binary("Author's avatar", related='author_id.avatar_128', depends=['author_id'], readonly=False)
    author_guest_id = fields.Many2one(string="Guest", comodel_name='mail.guest')
    is_current_user_or_guest_author = fields.Boolean(compute='_compute_is_current_user_or_guest_author')
    # recipients: include inactive partners (they may have been archived after
    # the message was sent, but they should remain visible in the relation)
    partner_ids = fields.Many2many('res.partner', string='Recipients', context={'active_test': False})
    # list of partner having a notification. Caution: list may change over time because of notif gc cron.
    # mainly usefull for testing
    notified_partner_ids = fields.Many2many(
        'res.partner', 'mail_notification', string='Partners with Need Action',
        context={'active_test': False}, depends=['notification_ids'], copy=False)
    needaction = fields.Boolean(
        'Need Action', compute='_compute_needaction', search='_search_needaction')
    has_error = fields.Boolean(
        'Has error', compute='_compute_has_error', search='_search_has_error')
    # notifications
    notification_ids = fields.One2many(
        'mail.notification', 'mail_message_id', 'Notifications',
        auto_join=True, copy=False, depends=['notified_partner_ids'])
    # user interface
    starred_partner_ids = fields.Many2many(
        'res.partner', 'mail_message_res_partner_starred_rel', string='Favorited By')
    pinned_at = fields.Datetime('Pinned', help='Datetime at which the message has been pinned')
    starred = fields.Boolean(
        'Starred', compute='_compute_starred', search='_search_starred', compute_sudo=False,
        help='Current user has a starred notification linked to this message')
    # tracking
    tracking_value_ids = fields.One2many(
        'mail.tracking.value', 'mail_message_id',
        string='Tracking values',
        groups="base.group_system",
        help='Tracked values are stored in a separate model. This field allow to reconstruct '
             'the tracking and to generate statistics on the model.')
    # mail gateway
    reply_to_force_new = fields.Boolean(
        'No threading for answers',
        help='If true, answers do not go in the original document discussion thread. Instead, it will check for the reply_to in tracking message-id and redirected accordingly. This has an impact on the generated message-id.')
    message_id = fields.Char('Message-Id', help='Message unique identifier', index='btree', readonly=True, copy=False)
    reply_to = fields.Char('Reply-To', help='Reply email address. Setting the reply_to bypasses the automatic thread creation.')
    mail_server_id = fields.Many2one('ir.mail_server', 'Outgoing mail server')
    # send notification information (for resend / reschedule)
    email_layout_xmlid = fields.Char('Layout', copy=False)  # xml id of layout
    email_add_signature = fields.Boolean(default=True)
    # `test_adv_activity`, `test_adv_activity_full`, `test_message_assignation_inbox`,...
    # By setting an inverse for mail.mail_message_id, the number of SQL queries done by `modified` is reduced.
    # 'mail.mail' inherits from `mail.message`: `_inherits = {'mail.message': 'mail_message_id'}`
    # Therefore, when changing a field on `mail.message`, this triggers the modification of the same field on `mail.mail`
    # By setting up the inverse one2many, we avoid to have to do a search to find the mails linked to the `mail.message`
    # as the cache value for this inverse one2many is up-to-date.
    # Besides for new messages, and messages never sending emails, there was no mail, and it was searching for nothing.
    mail_ids = fields.One2many('mail.mail', 'mail_message_id', string='Mails', groups="base.group_system")

    @api.depends('body', 'subject')
    def _compute_description(self):
        for message in self:
            if message.subject:
                message.description = message.subject
            else:
                message.description = message._get_message_preview(max_char=30)

    @api.depends('body')
    def _compute_preview(self):
        for message in self:
            message.preview = message._get_message_preview()

    @api.depends('author_id', 'author_guest_id')
    @api.depends_context('guest', 'uid')
    def _compute_is_current_user_or_guest_author(self):
        user = self.env.user
        guest = self.env['mail.guest']._get_guest_from_context()
        for message in self:
            if not user._is_public() and (message.author_id and message.author_id == user.partner_id):
                message.is_current_user_or_guest_author = True
            elif message.author_guest_id and message.author_guest_id == guest:
                message.is_current_user_or_guest_author = True
            else:
                message.is_current_user_or_guest_author = False

    def _compute_needaction(self):
        """ Need action on a mail.message = notified on my channel """
        my_messages = self.env['mail.notification'].sudo().search([
            ('mail_message_id', 'in', self.ids),
            ('res_partner_id', '=', self.env.user.partner_id.id),
            ('is_read', '=', False)]).mapped('mail_message_id')
        for message in self:
            message.needaction = message in my_messages

    @api.model
    def _search_needaction(self, operator, operand):
        is_read = False if operator == '=' and operand else True
        notification_ids = self.env['mail.notification']._search([('res_partner_id', '=', self.env.user.partner_id.id), ('is_read', '=', is_read)])
        return [('notification_ids', 'in', notification_ids)]

    def _compute_has_error(self):
        error_from_notification = self.env['mail.notification'].sudo().search([
            ('mail_message_id', 'in', self.ids),
            ('notification_status', 'in', ('bounce', 'exception'))]).mapped('mail_message_id')
        for message in self:
            message.has_error = message in error_from_notification

    def _search_has_error(self, operator, operand):
        if operator == '=' and operand:
            return [('notification_ids.notification_status', 'in', ('bounce', 'exception'))]
        return ['!', ('notification_ids.notification_status', 'in', ('bounce', 'exception'))]  # this wont work and will be equivalent to "not in" beacause of orm restrictions. Dont use "has_error = False"

    @api.depends('starred_partner_ids')
    @api.depends_context('uid')
    def _compute_starred(self):
        """ Compute if the message is starred by the current user. """
        # TDE FIXME: use SQL
        starred = self.sudo().filtered(lambda msg: self.env.user.partner_id in msg.starred_partner_ids)
        for message in self:
            message.starred = message in starred

    @api.model
    def _search_starred(self, operator, operand):
        if operator == '=' and operand:
            return [('starred_partner_ids', 'in', [self.env.user.partner_id.id])]
        return [('starred_partner_ids', 'not in', [self.env.user.partner_id.id])]

    # ------------------------------------------------------
    # CRUD / ORM
    # ------------------------------------------------------

    def init(self):
        self._cr.execute("""SELECT indexname FROM pg_indexes WHERE indexname = 'mail_message_model_res_id_idx'""")
        if not self._cr.fetchone():
            self._cr.execute("""CREATE INDEX mail_message_model_res_id_idx ON mail_message (model, res_id)""")
        self._cr.execute("""CREATE INDEX IF NOT EXISTS mail_message_model_res_id_id_idx ON mail_message (model, res_id, id)""")

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        """ Override that adds specific access rights of mail.message, to remove
        ids uid could not see according to our custom rules. Please refer to
        check_access_rule for more details about those rules.

        Non employees users see only message with subtype (aka do not see
        internal logs).

        After having received ids of a classic search, keep only:
        - if author_id == pid, uid is the author, OR
        - uid belongs to a notified channel, OR
        - uid is in the specified recipients, OR
        - uid has a notification on the message
        - otherwise: remove the id
        """
        # Rules do not apply to administrator
        if self.env.is_superuser():
            return super()._search(domain, offset, limit, order, access_rights_uid)

        # Non-employee see only messages with a subtype and not internal
        if not self.env['res.users'].has_group('base.group_user'):
            domain = self._get_search_domain_share() + domain

        # make the search query with the default rules
        query = super()._search(domain, offset, limit, order, access_rights_uid)

        # retrieve matching records and determine which ones are truly accessible
        self.flush_model(['model', 'res_id', 'author_id', 'message_type', 'partner_ids'])
        self.env['mail.notification'].flush_model(['mail_message_id', 'res_partner_id'])

        pid = self.env.user.partner_id.id
        ids = []
        allowed_ids = set()
        model_ids = defaultdict(lambda: defaultdict(set))

        rel_alias = query.make_alias(self._table, 'partner_ids')
        query.add_join("LEFT JOIN", rel_alias, 'mail_message_res_partner_rel', SQL(
            "%s = %s AND %s = %s",
            SQL.identifier(self._table, 'id'),
            SQL.identifier(rel_alias, 'mail_message_id'),
            SQL.identifier(rel_alias, 'res_partner_id'),
            pid,
        ))
        notif_alias = query.make_alias(self._table, 'notification_ids')
        query.add_join("LEFT JOIN", notif_alias, 'mail_notification', SQL(
            "%s = %s AND %s = %s",
            SQL.identifier(self._table, 'id'),
            SQL.identifier(notif_alias, 'mail_message_id'),
            SQL.identifier(notif_alias, 'res_partner_id'),
            pid,
        ))
        self.env.cr.execute(query.select(
            SQL.identifier(self._table, 'id'),
            SQL.identifier(self._table, 'model'),
            SQL.identifier(self._table, 'res_id'),
            SQL.identifier(self._table, 'author_id'),
            SQL.identifier(self._table, 'message_type'),
            SQL(
                "COALESCE(%s, %s)",
                SQL.identifier(rel_alias, 'res_partner_id'),
                SQL.identifier(notif_alias, 'res_partner_id'),
            ),
        ))
        for id_, model, res_id, author_id, message_type, partner_id in self.env.cr.fetchall():
            ids.append(id_)
            if author_id == pid:
                allowed_ids.add(id_)
            elif partner_id == pid:
                allowed_ids.add(id_)
            elif model and res_id and message_type != 'user_notification':
                model_ids[model][res_id].add(id_)

        allowed_ids.update(self._find_allowed_doc_ids(model_ids))
        allowed = self.browse(id_ for id_ in ids if id_ in allowed_ids)
        return allowed._as_query(order)

    @api.model
    def _find_allowed_model_wise(self, doc_model, doc_dict):
        doc_ids = list(doc_dict)
        allowed_doc_ids = self.env[doc_model].with_context(active_test=False).search([('id', 'in', doc_ids)]).ids
        return set([message_id for allowed_doc_id in allowed_doc_ids for message_id in doc_dict[allowed_doc_id]])

    @api.model
    def _find_allowed_doc_ids(self, model_ids):
        IrModelAccess = self.env['ir.model.access']
        allowed_ids = set()
        for doc_model, doc_dict in model_ids.items():
            if not IrModelAccess.check(doc_model, 'read', False):
                continue
            allowed_ids |= self._find_allowed_model_wise(doc_model, doc_dict)
        return allowed_ids

    def check_access_rule(self, operation):
        """ Access rules of mail.message:
            - read: if
                - author_id == pid, uid is the author OR
                - create_uid == uid, uid is the creator OR
                - uid is in the recipients (partner_ids) OR
                - uid has been notified (needaction) OR
                - uid have read access to the related document if model, res_id
                - otherwise: raise
            - create: if
                - no model, no res_id (private message) OR
                - pid in message_follower_ids if model, res_id OR
                - uid can read the parent OR
                - uid have write or create access on the related document if model, res_id, OR
                - otherwise: raise
            - write: if
                - author_id == pid, uid is the author, OR
                - uid is in the recipients (partner_ids) OR
                - uid has write or create access on the related document if model, res_id
                - otherwise: raise
            - unlink: if
                - uid has write or create access on the related document
                - otherwise: raise

        Specific case: non employee users see only messages with subtype (aka do
        not see internal logs).
        """
        def _generate_model_record_ids(msg_val, msg_ids):
            """ :param model_record_ids: {'model': {'res_id': (msg_id, msg_id)}, ... }
                :param message_values: {'msg_id': {'model': .., 'res_id': .., 'author_id': ..}}
            """
            model_record_ids = {}
            for id in msg_ids:
                vals = msg_val.get(id, {})
                if vals.get('model') and vals.get('res_id'):
                    model_record_ids.setdefault(vals['model'], set()).add(vals['res_id'])
            return model_record_ids

        if self.env.is_superuser():
            return

        # just in case there are ir.rules
        super().check_access_rule(operation)

        # Non employees see only messages with a subtype (aka, not internal logs)
        if not self.env['res.users'].has_group('base.group_user'):
            self._cr.execute('''SELECT DISTINCT message.id, message.subtype_id, subtype.internal
                                FROM "%s" AS message
                                LEFT JOIN "mail_message_subtype" as subtype
                                ON message.subtype_id = subtype.id
                                WHERE message.message_type = %%s AND
                                    (message.is_internal IS TRUE OR message.subtype_id IS NULL OR subtype.internal IS TRUE) AND
                                    message.id = ANY (%%s)''' % (self._table), ('comment', self.ids,))
            if self._cr.fetchall():
                raise AccessError(
                    _('The requested operation cannot be completed due to security restrictions. Please contact your system administrator.\n\n(Document type: %s, Operation: %s)', self._description, operation)
                    + ' - ({} {}, {} {})'.format(_('Records:'), self.ids[:6], _('User:'), self._uid)
                )

        # Read mail_message.ids to have their values
        message_values = dict((message_id, {}) for message_id in self.ids)

        self.flush_recordset(['model', 'res_id', 'author_id', 'create_uid', 'parent_id', 'message_type', 'partner_ids'])
        self.env['mail.notification'].flush_model(['mail_message_id', 'res_partner_id'])

        if operation == 'read':
            self._cr.execute("""
                SELECT DISTINCT m.id, m.model, m.res_id, m.author_id, m.create_uid,
                                m.parent_id,
                                COALESCE(partner_rel.res_partner_id, needaction_rel.res_partner_id),
                                m.message_type as message_type
                FROM "%s" m
                LEFT JOIN "mail_message_res_partner_rel" partner_rel
                ON partner_rel.mail_message_id = m.id AND partner_rel.res_partner_id = %%(pid)s
                LEFT JOIN "mail_notification" needaction_rel
                ON needaction_rel.mail_message_id = m.id AND needaction_rel.res_partner_id = %%(pid)s
                WHERE m.id = ANY (%%(ids)s)""" % self._table, dict(pid=self.env.user.partner_id.id, ids=self.ids))
            for mid, rmod, rid, author_id, create_uid, parent_id, partner_id, message_type in self._cr.fetchall():
                message_values[mid] = {
                    'model': rmod,
                    'res_id': rid,
                    'author_id': author_id,
                    'create_uid': create_uid,
                    'parent_id': parent_id,
                    'notified': any((message_values[mid].get('notified'), partner_id)),
                    'message_type': message_type,
                }
        elif operation == 'write':
            self._cr.execute("""
                SELECT DISTINCT m.id, m.model, m.res_id, m.author_id, m.parent_id,
                                COALESCE(partner_rel.res_partner_id, needaction_rel.res_partner_id),
                                m.message_type as message_type
                FROM "%s" m
                LEFT JOIN "mail_message_res_partner_rel" partner_rel
                ON partner_rel.mail_message_id = m.id AND partner_rel.res_partner_id = %%(pid)s
                LEFT JOIN "mail_notification" needaction_rel
                ON needaction_rel.mail_message_id = m.id AND needaction_rel.res_partner_id = %%(pid)s
                WHERE m.id = ANY (%%(ids)s)""" % self._table, dict(pid=self.env.user.partner_id.id, uid=self.env.user.id, ids=self.ids))
            for mid, rmod, rid, author_id, parent_id, partner_id, message_type in self._cr.fetchall():
                message_values[mid] = {
                    'model': rmod,
                    'res_id': rid,
                    'author_id': author_id,
                    'parent_id': parent_id,
                    'notified': any((message_values[mid].get('notified'), partner_id)),
                    'message_type': message_type,
                }
        elif operation in ('create', 'unlink'):
            self._cr.execute("""SELECT DISTINCT id, model, res_id, author_id, parent_id, message_type FROM "%s" WHERE id = ANY (%%s)""" % self._table, (self.ids,))
            for mid, rmod, rid, author_id, parent_id, message_type in self._cr.fetchall():
                message_values[mid] = {
                    'model': rmod,
                    'res_id': rid,
                    'author_id': author_id,
                    'parent_id': parent_id,
                    'message_type': message_type,
                }
        else:
            raise ValueError(_('Wrong operation name (%s)', operation))

        # Author condition (READ, WRITE, CREATE (private))
        author_ids = []
        if operation == 'read':
            author_ids = [mid for mid, message in message_values.items()
                          if (
                                message.get('author_id') and
                                message.get('author_id') == self.env.user.partner_id.id
                            ) or (
                                message.get('create_uid') and
                                message.get('create_uid') == self.env.uid
                            )
                         ]
        elif operation == 'write':
            author_ids = [mid for mid, message in message_values.items() if message.get('author_id') == self.env.user.partner_id.id]
        elif operation == 'create':
            author_ids = [mid for mid, message in message_values.items()
                          if not self.is_thread_message(message)]

        messages_to_check = self.ids
        messages_to_check = set(messages_to_check).difference(set(author_ids))
        if not messages_to_check:
            return

        # Recipients condition, for read and write (partner_ids)
        # keep on top, usefull for systray notifications
        notified_ids = []
        model_record_ids = _generate_model_record_ids(message_values, messages_to_check)
        if operation in ['read', 'write']:
            notified_ids = [mid for mid, message in message_values.items() if message.get('notified')]

        messages_to_check = set(messages_to_check).difference(set(notified_ids))
        if not messages_to_check:
            return

        # CRUD: Access rights related to the document
        document_related_ids = []
        document_related_candidate_ids = [
            mid for mid, message in message_values.items()
            if (message.get('model') and message.get('res_id') and
                message.get('message_type') != 'user_notification')
        ]
        model_record_ids = _generate_model_record_ids(message_values, document_related_candidate_ids)
        for model, doc_ids in model_record_ids.items():
            DocumentModel = self.env[model]
            if hasattr(DocumentModel, '_get_mail_message_access'):
                check_operation = DocumentModel._get_mail_message_access(doc_ids, operation)  ## why not giving model here?
            else:
                check_operation = self.env['mail.thread']._get_mail_message_access(doc_ids, operation, model_name=model)
            records = DocumentModel.browse(doc_ids)
            records.check_access_rights(check_operation)
            mids = records.browse(doc_ids)._filter_access_rules(check_operation)
            document_related_ids += [
                mid for mid, message in message_values.items()
                if (
                    message.get('model') == model and
                    message.get('res_id') in mids.ids and
                    message.get('message_type') != 'user_notification'
                )
            ]

        messages_to_check = messages_to_check.difference(set(document_related_ids))

        if not messages_to_check:
            return

        # Parent condition, for create (check for received notifications for the created message parent)
        notified_ids = []
        if operation == 'create':
            # TDE: probably clean me
            parent_ids = [message.get('parent_id') for message in message_values.values()
                          if message.get('parent_id')]
            self._cr.execute("""SELECT DISTINCT m.id, partner_rel.res_partner_id FROM "%s" m
                LEFT JOIN "mail_message_res_partner_rel" partner_rel
                ON partner_rel.mail_message_id = m.id AND partner_rel.res_partner_id = (%%s)
                WHERE m.id = ANY (%%s)""" % self._table, (self.env.user.partner_id.id, parent_ids,))
            not_parent_ids = [mid[0] for mid in self._cr.fetchall() if mid[1]]
            notified_ids += [mid for mid, message in message_values.items()
                             if message.get('parent_id') in not_parent_ids]

        messages_to_check = messages_to_check.difference(set(notified_ids))
        if not messages_to_check:
            return

        # Recipients condition for create (message_follower_ids)
        if operation == 'create':
            for doc_model, doc_ids in model_record_ids.items():
                followers = self.env['mail.followers'].sudo().search([
                    ('res_model', '=', doc_model),
                    ('res_id', 'in', list(doc_ids)),
                    ('partner_id', '=', self.env.user.partner_id.id),
                    ])
                fol_mids = [follower.res_id for follower in followers]
                notified_ids += [mid for mid, message in message_values.items()
                                 if message.get('model') == doc_model and
                                 message.get('res_id') in fol_mids and
                                 message.get('message_type') != 'user_notification'
                                 ]

        messages_to_check = messages_to_check.difference(set(notified_ids))
        if not messages_to_check:
            return

        if not self.browse(messages_to_check).exists():
            return
        raise AccessError(
            _('The requested operation cannot be completed due to security restrictions. Please contact your system administrator.\n\n(Document type: %s, Operation: %s)', self._description, operation)
            + ' - ({} {}, {} {})'.format(_('Records:'), list(messages_to_check)[:6], _('User:'), self._uid)
        )

    def _validate_access_for_current_persona(self, operation):
        if not self:
            return False
        self.ensure_one()
        self.sudo(False).check_access_rule(operation)
        self.sudo(False).check_access_rights(operation)
        return True

    @api.model_create_multi
    def create(self, values_list):
        tracking_values_list = []
        for values in values_list:
            if 'email_from' not in values:  # needed to compute reply_to
                _author_id, email_from = self.env['mail.thread']._message_compute_author(values.get('author_id'), email_from=None, raise_on_email=False)
                values['email_from'] = email_from
            if not values.get('message_id'):
                values['message_id'] = self._get_message_id(values)
            if 'reply_to' not in values:
                values['reply_to'] = self._get_reply_to(values)
            if 'record_name' not in values and 'default_record_name' not in self.env.context:
                values['record_name'] = self._get_record_name(values)

            if not values.get('attachment_ids'):
                values['attachment_ids'] = []
            # extract base64 images
            if 'body' in values:
                Attachments = self.env['ir.attachment'].with_context(clean_context(self._context))
                data_to_url = {}
                def base64_to_boundary(match):
                    key = match.group(2)
                    if not data_to_url.get(key):
                        name = match.group(4) if match.group(4) else 'image%s' % len(data_to_url)
                        try:
                            attachment = Attachments.create({
                                'name': name,
                                'datas': match.group(2),
                                'res_model': values.get('model'),
                                'res_id': values.get('res_id'),
                            })
                        except binascii_error:
                            _logger.warning("Impossible to create an attachment out of badly formated base64 embedded image. Image has been removed.")
                            return match.group(3)  # group(3) is the url ending single/double quote matched by the regexp
                        else:
                            attachment.generate_access_token()
                            values['attachment_ids'].append((4, attachment.id))
                            data_to_url[key] = ['/web/image/%s?access_token=%s' % (attachment.id, attachment.access_token), name]
                    return '%s%s alt="%s"' % (data_to_url[key][0], match.group(3), data_to_url[key][1])
                values['body'] = _image_dataurl.sub(base64_to_boundary, tools.ustr(values['body']))

            # delegate creation of tracking after the create as sudo to avoid access rights issues
            tracking_values_list.append(values.pop('tracking_value_ids', False))

        messages = super(Message, self).create(values_list)

        # link back attachments to records, to filter out attachments linked to
        # the same records as the message (considered as ok if message is ok)
        # and check rights on other documents
        attachments_tocheck = self.env['ir.attachment']
        doc_to_attachment_ids = defaultdict(set)
        if all(isinstance(command, int) or command[0] in (4, 6)
               for values in values_list
               for command in values['attachment_ids']):
            for values in values_list:
                message_attachment_ids = set()
                for command in values['attachment_ids']:
                    if isinstance(command, int):
                        message_attachment_ids.add(command)
                    elif command[0] == 6:
                        message_attachment_ids |= set(command[2])
                    else:  # command[0] == 4:
                        message_attachment_ids.add(command[1])
                if message_attachment_ids:
                    key = (values.get('model'), values.get('res_id'))
                    doc_to_attachment_ids[key] |= message_attachment_ids

            attachment_ids_all = {
                attachment_id
                for doc_attachment_ids in doc_to_attachment_ids
                for attachment_id in doc_attachment_ids
            }
            AttachmentSudo = self.env['ir.attachment'].sudo().with_prefetch(list(attachment_ids_all))
            for (model, res_id), doc_attachment_ids in doc_to_attachment_ids.items():
                # check only attachments belonging to another model, access already
                # checked on message for other attachments
                attachments_tocheck += AttachmentSudo.browse(doc_attachment_ids).filtered(
                    lambda att: att.res_model != model or att.res_id != res_id
                ).sudo(False)
        else:
            attachments_tocheck = messages.attachment_ids  # fallback on read if any unknown command
        if attachments_tocheck:
            attachments_tocheck.check('read')

        for message, values, tracking_values_cmd in zip(messages, values_list, tracking_values_list):
            if tracking_values_cmd:
                vals_lst = [dict(cmd[2], mail_message_id=message.id) for cmd in tracking_values_cmd if len(cmd) == 3 and cmd[0] == 0]
                other_cmd = [cmd for cmd in tracking_values_cmd if len(cmd) != 3 or cmd[0] != 0]
                if vals_lst:
                    self.env['mail.tracking.value'].sudo().create(vals_lst)
                if other_cmd:
                    message.sudo().write({'tracking_value_ids': tracking_values_cmd})

            if message.is_thread_message(values):
                message._invalidate_documents(values.get('model'), values.get('res_id'))

        return messages

    def read(self, fields=None, load='_classic_read'):
        """ Override to explicitely call check_access_rule, that is not called
            by the ORM. It instead directly fetches ir.rules and apply them. """
        self.check_access_rule('read')
        return super(Message, self).read(fields=fields, load=load)

    def fetch(self, field_names):
        # This freaky hack is aimed at reading data without the overhead of
        # checking that "self" is accessible, which is already done above in
        # methods read() and _search(). It reproduces the existing behavior
        # before the introduction of method fetch(), where the low-lever
        # reading method _read() did not enforce any actual permission.
        self = self.sudo()
        return super().fetch(field_names)

    def write(self, vals):
        record_changed = 'model' in vals or 'res_id' in vals
        if record_changed or 'message_type' in vals:
            self._invalidate_documents()
        res = super(Message, self).write(vals)
        if vals.get('attachment_ids'):
            for mail in self:
                mail.attachment_ids.check(mode='read')
        if 'notification_ids' in vals or record_changed:
            self._invalidate_documents()
        return res

    def unlink(self):
        # cascade-delete attachments that are directly attached to the message (should only happen
        # for mail.messages that act as parent for a standalone mail.mail record).
        # the cache of the related document doesn't need to be invalidate (see @_invalidate_documents)
        # because the unlink method invalidates the whole cache anyway
        if not self:
            return True
        self.check_access_rule('unlink')
        self.mapped('attachment_ids').filtered(
            lambda attach: attach.res_model == self._name and (attach.res_id in self.ids or attach.res_id == 0)
        ).unlink()
        messages_by_partner = defaultdict(lambda: self.env['mail.message'])
        partners_with_user = self.partner_ids.filtered('user_ids')
        for elem in self:
            for partner in (
                elem.partner_ids & partners_with_user | elem.notification_ids.author_id
            ):
                messages_by_partner[partner] |= elem

        # Notify front-end of messages deletion for partners having a user
        if messages_by_partner:
            self.env['bus.bus']._sendmany([
                (partner, 'mail.message/delete', {'message_ids': messages.ids})
                for partner, messages in messages_by_partner.items()
            ])

        return super(Message, self).unlink()

    def export_data(self, fields_to_export):
        if not self.env.is_admin():
            raise AccessError(_("Only administrators are allowed to export mail message"))

        return super(Message, self).export_data(fields_to_export)

    # ------------------------------------------------------
    # ACTIONS
    # ----------------------------------------------------

    def action_open_document(self):
        """ Opens the related record based on the model and ID """
        self.ensure_one()
        return {
            'res_id': self.res_id,
            'res_model': self.model,
            'target': 'current',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
        }

    # ------------------------------------------------------
    # DISCUSS API
    # ------------------------------------------------------

    @api.model
    def mark_all_as_read(self, domain=None):
        # not really efficient method: it does one db request for the
        # search, and one for each message in the result set is_read to True in the
        # current notifications from the relation.
        notif_domain = [
            ('res_partner_id', '=', self.env.user.partner_id.id),
            ('is_read', '=', False)]
        if domain:
            messages = self.search(domain)
            messages.set_message_done()
            return messages.ids

        notifications = self.env['mail.notification'].sudo().search_fetch(notif_domain, ['mail_message_id'])
        notifications.write({'is_read': True})

        self.env['bus.bus']._sendone(self.env.user.partner_id, 'mail.message/mark_as_read', {
            'message_ids': notifications.mail_message_id.ids,
            'needaction_inbox_counter': self.env.user.partner_id._get_needaction_count(),
        })

    def set_message_done(self):
        """ Remove the needaction from messages for the current partner. """
        partner_id = self.env.user.partner_id

        notifications = self.env['mail.notification'].sudo().search_fetch([
            ('mail_message_id', 'in', self.ids),
            ('res_partner_id', '=', partner_id.id),
            ('is_read', '=', False),
        ], ['mail_message_id'])

        if not notifications:
            return

        notifications.write({'is_read': True})

        # notifies changes in messages through the bus.
        self.env['bus.bus']._sendone(partner_id, 'mail.message/mark_as_read', {
            'message_ids': notifications.mail_message_id.ids,
            'needaction_inbox_counter': self.env.user.partner_id._get_needaction_count(),
        })

    @api.model
    def unstar_all(self):
        """ Unstar messages for the current partner. """
        partner = self.env.user.partner_id

        starred_messages = self.search([('starred_partner_ids', 'in', partner.id)])
        partner.starred_message_ids -= starred_messages
        self.env['bus.bus']._sendone(partner, 'mail.message/toggle_star', {
            'message_ids': starred_messages.ids,
            'starred': False,
        })

    def toggle_message_starred(self):
        """ Toggle messages as (un)starred. Technically, the notifications related
            to uid are set to (un)starred.
        """
        # a user should always be able to star a message they can read
        self.check_access_rule('read')
        starred = not self.starred
        partner = self.env.user.partner_id
        if starred:
            partner.starred_message_ids |= self
        else:
            partner.starred_message_ids -= self

        self.env['bus.bus']._sendone(partner, 'mail.message/toggle_star', {
            'message_ids': [self.id],
            'starred': starred,
        })

    def _message_reaction(self, content, action):
        self.ensure_one()
        partner, guest = self.env["res.partner"]._get_current_persona()
        # search for existing reaction
        domain = [
            ("message_id", "=", self.id),
            ("partner_id", "=", partner.id),
            ("guest_id", "=", guest.id),
            ("content", "=", content),
        ]
        reaction = self.env["mail.message.reaction"].search(domain)
        # create/unlink reaction if necessary
        if action == "add" and not reaction:
            create_values = {
                "message_id": self.id,
                "content": content,
                "partner_id": partner.id,
                "guest_id": guest.id,
            }
            self.env["mail.message.reaction"].create(create_values)
        if action == "remove" and reaction:
            reaction.unlink()
        # format result
        group_domain = [("message_id", "=", self.id), ("content", "=", content)]
        count = self.env["mail.message.reaction"].search_count(group_domain)
        group_command = "ADD" if count > 0 else "DELETE"
        persona = guest or partner
        personas = []
        if persona:
            persona_data = {"id": persona.id, "type": "guest" if guest else "partner"}
            if group_command == "ADD":
                persona_data.update({"name": persona.name, "write_date": persona.write_date})
            personas = [("ADD" if action == "add" else "DELETE", persona_data)]
        group_values = {
            "content": content,
            "count": count,
            "personas": personas,
            "message": {"id": self.id},
        }
        payload = {"Message": {"id": self.id, "reactions": [(group_command, group_values)]}}
        self.env["bus.bus"]._sendone(self._bus_notification_target(), "mail.record/insert", payload)

    # ------------------------------------------------------
    # MESSAGE READ / FETCH / FAILURE API
    # ------------------------------------------------------

    def _message_format(self, fnames, format_reply=True):
        """Reads values from messages and formats them for the web client."""
        vals_list = self._read_format(fnames)
        thread_ids_by_model_name = defaultdict(set)
        for message in self:
            if message.model and message.res_id:
                thread_ids_by_model_name[message.model].add(message.res_id)
        for vals in vals_list:
            message_sudo = self.browse(vals['id']).sudo().with_prefetch(self.ids)
            author = False
            if message_sudo.author_guest_id:
                author = {
                    'id': message_sudo.author_guest_id.id,
                    'name': message_sudo.author_guest_id.name,
                    'type': "guest",
                }
            elif message_sudo.author_id:
                author = message_sudo.author_id.mail_partner_format({'id': True, 'name': True, 'is_company': True, 'user': {"id": True}}).get(message_sudo.author_id)
            record_sudo = False
            if message_sudo.model and message_sudo.res_id:
                record_sudo = self.env[message_sudo.model].browse(message_sudo.res_id).sudo()
                record_name = record_sudo.with_prefetch(thread_ids_by_model_name[message_sudo.model]).display_name
                default_subject = record_name
                if hasattr(record_sudo, '_message_compute_subject'):
                    default_subject = record_sudo._message_compute_subject()
            else:
                record_name = False
                default_subject = False
            reactions_per_content = defaultdict(self.env['mail.message.reaction'].sudo().browse)
            for reaction in message_sudo.reaction_ids:
                reactions_per_content[reaction.content] |= reaction
            reaction_groups = [{
                'content': content,
                'count': len(reactions),
                'personas': [{'id': guest.id, 'name': guest.name, 'type': "guest"} for guest in reactions.guest_id] + [{'id': partner.id, 'name': partner.name, 'type': "partner"} for partner in reactions.partner_id],
                'message': {'id': message_sudo.id},
            } for content, reactions in reactions_per_content.items()]
            allowed_tracking_ids = message_sudo.tracking_value_ids.filtered(lambda tracking: not tracking.field_groups or self.env.is_superuser() or self.user_has_groups(tracking.field_groups))
            displayed_tracking_ids = allowed_tracking_ids
            if record_sudo and hasattr(record_sudo, '_track_filter_for_display'):
                displayed_tracking_ids = record_sudo._track_filter_for_display(displayed_tracking_ids)
            vals.update(message_sudo._message_format_extras(format_reply))
            vals.update({
                'author': author,
                'default_subject': default_subject,
                'notifications': message_sudo.notification_ids._filtered_for_web_client()._notification_format(),
                'attachments': sorted(message_sudo.attachment_ids._attachment_format(), key=lambda a: a["id"]),
                'trackingValues': displayed_tracking_ids._tracking_value_format(),
                'linkPreviews': message_sudo.link_preview_ids._link_preview_format(),
                'reactions': reaction_groups,
                'pinned_at': message_sudo.pinned_at,
                'record_name': record_name,
                'create_date': message_sudo.create_date,
                'write_date': message_sudo.write_date,
            })
        return vals_list

    def _message_format_extras(self, format_reply):
        self.ensure_one()
        return {}

    @api.model
    def _message_fetch(self, domain, search_term=None, before=None, after=None, around=None, limit=30):
        res = {}
        if search_term:
            # we replace every space by a % to avoid hard spacing matching
            search_term = search_term.replace(" ", "%")
            domain = expression.AND([domain, expression.OR([
                # sudo: access to attachment is allowed if you have access to the parent model
                [("attachment_ids", "in", self.env["ir.attachment"].sudo()._search([("name", "ilike", search_term)]))],
                [("body", "ilike", search_term)],
                [("subject", "ilike", search_term)],
                [("subtype_id.description", "ilike", search_term)],
            ])])
            res["count"] = self.search_count(domain)
        if around:
            messages_before = self.search(domain=[*domain, ('id', '<=', around)], limit=limit // 2, order="id DESC")
            messages_after = self.search(domain=[*domain, ('id', '>', around)], limit=limit // 2, order='id ASC')
            return {**res, "messages": (messages_after + messages_before).sorted('id', reverse=True)}
        if before:
            domain = expression.AND([domain, [('id', '<', before)]])
        if after:
            domain = expression.AND([domain, [('id', '>', after)]])
        res["messages"] = self.search(domain, limit=limit, order='id ASC' if after else 'id DESC')
        if after:
            res["messages"] = res["messages"].sorted('id', reverse=True)
        return res

    def message_format(self, format_reply=True, msg_vals=None):
        """ Get the message values in the format for web client. Since message
        values can be broadcasted, computed fields MUST NOT BE READ and
        broadcasted.

        :param msg_vals: dictionary of values used to create the message. If
          given it may be used to access values related to ``message`` without
          accessing it directly. It lessens query count in some optimized use
          cases by avoiding access message content in db;

        :returns list(dict).
             Example :
                {
                    'body': HTML content of the message
                    'model': u'res.partner',
                    'record_name': u'Agrolait',
                    'attachments': [
                        {
                            'file_type_icon': u'webimage',
                            'id': 45,
                            'name': u'sample.png',
                            'filename': u'sample.png'
                        }
                    ],
                    'needaction_partner_ids': [], # list of partner ids
                    'res_id': 7,
                    'trackingValues': [
                        {
                            'changedField': "Customer",
                            'id': 2965,
                            'fieldName': 'partner_id',
                            'fieldType': 'char',
                            'newValue': {
                                'currencyId': "",
                                'value': "Axelor",
                            ],
                            'oldValue': {
                                'currencyId': "",
                                'value': "",
                            ],
                        }
                    ],
                    'author_id': (3, u'Administrator'),
                    'email_from': 'sacha@pokemon.com' # email address or False
                    'subtype_id': (1, u'Discussions'),
                    'date': '2015-06-30 08:22:33',
                    'partner_ids': [[7, "Sacha Du Bourg-Palette"]], # list of partner convert_to_read
                    'message_type': u'comment',
                    'id': 59,
                    'subject': False
                    'is_note': True # only if the message is a note (subtype == note)
                    'is_discussion': False # only if the message is a discussion (subtype == discussion)
                    'parentMessage': {...}, # formatted message that this message is a reply to. Only present if format_reply is True
                }
        """
        self.check_access_rule('read')
        vals_list = self._message_format(self._get_message_format_fields(), format_reply=format_reply)

        com_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment')
        note_id = self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note')

        # fetch scheduled notifications once, only if msg_vals is not given to
        # avoid useless queries when notifying Inbox right after a message_post
        scheduled_dt_by_msg_id = {}
        if msg_vals:
            scheduled_dt_by_msg_id = {msg.id: msg_vals.get('scheduled_date') for msg in self}
        elif self:
            schedulers = self.env['mail.message.schedule'].sudo().search([
                ('mail_message_id', 'in', self.ids)
            ])
            for scheduler in schedulers:
                scheduled_dt_by_msg_id[scheduler.mail_message_id.id] = scheduler.scheduled_datetime

        for vals in vals_list:
            message_sudo = self.browse(vals['id']).sudo().with_prefetch(self.ids)
            notifs = message_sudo.notification_ids.filtered(lambda n: n.res_partner_id)
            vals.update({
                'needaction_partner_ids': notifs.filtered(lambda n: not n.is_read).res_partner_id.ids,
                'history_partner_ids': notifs.filtered(lambda n: n.is_read).res_partner_id.ids,
                'is_note': message_sudo.subtype_id.id == note_id,
                'is_discussion': message_sudo.subtype_id.id == com_id,
                'subtype_description': message_sudo.subtype_id.description,
                'recipients': [{'id': p.id, 'name': p.name, 'type': "partner"} for p in message_sudo.partner_ids],
                'scheduledDatetime': scheduled_dt_by_msg_id.get(vals['id'], False),
            })
            if vals['model'] and self.env[vals['model']]._original_module:
                vals['module_icon'] = modules.module.get_module_icon(self.env[vals['model']]._original_module)
        return vals_list

    @api.model
    def _message_format_personalized_prepare(self, messages_formatted, partner_ids=None):
        """ Prepare message to be personalized by partner.

        This method add partner information in batch to the messages so that the
        messages could be personalized for each partner by using
        _message_format_personalize with no or a limited number of queries.

        For example, it gathers all followers of the record related to the messages
        in one go (or limit it to the partner given in parameter), so that the method
        _message_format_personalize could then personalize each message for each partner.

        Note that followers for message related to discuss.channel are not fetched.

        :param list messages_formatted: list of message formatted using the method
            message_format
        :param list partner_ids: (optional) limit value computation to the partners
            of the given list; if not set, all partners are considered (all partners
            following each record will be included in follower_id_by_partner_id).

        :return: list of messages_formatted with added value:
            'follower_id_by_partner_id': dict partner_id -> follower_id of the record
        """
        domain = expression.OR([
            [('res_model', '=', model), ('res_id', 'in', list({value['res_id'] for value in values}))]
            for model, values in tools_groupby(
                (vals for vals in messages_formatted
                 if vals.get("res_id") and vals.get("model") not in {None, False, '', 'discuss.channel'}),
                key=lambda r: r["model"]
            )
        ])
        if partner_ids:
            domain = expression.AND([domain, [('partner_id', 'in', partner_ids)]])
        records_followed = self.env['mail.followers'].sudo().search(domain)
        followers_by_record_ref = (
            {(res_model, res_id): {value['partner_id'][0]: value['id'] for value in values}
             for (res_model, res_id), values in tools_groupby(
                records_followed.read(['res_id', 'res_model', 'partner_id']),
                key=lambda r: (r["res_model"], r['res_id'])
            )})
        for vals in messages_formatted:
            vals['follower_id_by_partner_id'] = followers_by_record_ref.get((vals['model'], vals['res_id']), dict())
        return messages_formatted

    def _message_format_personalize(self, partner_id, messages_formatted=None, format_reply=True, msg_vals=None):
        """ Personalize the messages for the partner.

        :param integer partner_id: id of the partner to personalize the messages for
        :param list messages_formatted: (optional) list of message formatted using
            the method _message_format_personalized_prepare.
            If not provided message_format is called on self with the 2 next parameters
            to format the messages and then the messages are personalized.
        :param bool format_reply: (optional) see method message_format
        :param dict msg_vals: (optional) see method message_format
        :return: list of messages_formatted personalized for the partner
        """
        if not messages_formatted:
            messages_formatted = self.message_format(format_reply=format_reply, msg_vals=msg_vals)
            self._message_format_personalized_prepare(messages_formatted, [partner_id])
        for vals in messages_formatted:
            # set value for user being a follower, fallback to False if not prepared
            follower_id_by_pid = vals.pop('follower_id_by_partner_id', {})
            vals['user_follower_id'] = follower_id_by_pid.get(partner_id, False)
        return messages_formatted

    def _get_message_format_fields(self):
        return [
            'id', 'body', 'date', 'email_from',  # base message fields
            'message_type', 'subtype_id', 'subject',  # message specific
            'model', 'res_id', 'record_name',  # document related
            'starred_partner_ids',  # list of partner ids for whom the message is starred
        ]

    def _message_notification_format(self):
        """Returns the current messages and their corresponding notifications in
        the format expected by the web client.

        Notifications hold the information about each recipient of a message: if
        the message was successfully sent or if an exception or bounce occurred.
        """
        return [{
            'author': {'id': message.author_id.id, 'type': "partner"} if message.author_id else False,
            'id': message.id,
            'res_id': message.res_id,
            'model': message.model,
            'res_model_name': message.env['ir.model']._get(message.model).display_name,
            'date': message.date,
            'message_type': message.message_type,
            'body': message.body,
            'notifications': message.notification_ids._filtered_for_web_client()._notification_format(),
        } for message in self]

    def _notify_message_notification_update(self):
        """Send bus notifications to update status of notifications in the web
        client. Purpose is to send the updated status per author."""
        messages = self.env['mail.message']
        for message in self:
            # Check if user has access to the record before displaying a notification about it.
            # In case the user switches from one company to another, it might happen that they don't
            # have access to the record related to the notification. In this case, we skip it.
            # YTI FIXME: check allowed_company_ids if necessary
            if message.model and message.res_id:
                record = self.env[message.model].browse(message.res_id)
                try:
                    record.check_access_rights('read')
                    record.check_access_rule('read')
                except AccessError:
                    continue
                else:
                    messages += message
        messages_per_partner = defaultdict(lambda: self.env['mail.message'])
        for message in messages:
            if not self.env.user._is_public():
                messages_per_partner[self.env.user.partner_id] |= message
            if message.author_id and not any(user._is_public() for user in message.author_id.with_context(active_test=False).user_ids):
                messages_per_partner[message.author_id] |= message
        updates = [
            (partner, 'mail.message/notification_update', {'elements': messages._message_notification_format()})
            for partner, messages in messages_per_partner.items()
        ]
        self.env['bus.bus']._sendmany(updates)

    def _bus_notification_target(self):
        self.ensure_one()
        return self.env.user.partner_id

    # ------------------------------------------------------
    # TOOLS
    # ------------------------------------------------------

    def _cleanup_side_records(self):
        """ Clean related data: notifications, stars, ... to avoid lingering
        notifications / unreachable counters with void messages notably. """
        self.write({
            'starred_partner_ids': [(5, 0, 0)],
            'notification_ids': [(5, 0, 0)],
        })

    def _filter_empty(self):
        """ Return subset of "void" messages """
        return self.filtered(
            lambda msg:
                (not msg.body or tools.is_html_empty(msg.body)) and
                (not msg.subtype_id or not msg.subtype_id.description) and
                not msg.attachment_ids and
                not msg.tracking_value_ids
        )

    def _get_message_preview(self, max_char=190):
        """Returns an unformatted version of the message body. Unless `max_char=0` is passed,
        output will be capped at max_char characters with a ' [...]' suffix if applicable.
        Default `max_char` is the longest known mail client preview length (Outlook 2013)."""
        self.ensure_one()

        plaintext_ct = tools.html_to_inner_content(self.body)
        return textwrap.shorten(plaintext_ct, max_char) if max_char else plaintext_ct

    @api.model
    def _get_record_name(self, values):
        """ Return the related document name, using display_name. It is done using
            SUPERUSER_ID, to be sure to have the record name correctly stored. """
        model = values.get('model', self.env.context.get('default_model'))
        res_id = values.get('res_id', self.env.context.get('default_res_id'))
        if not model or not res_id or model not in self.env:
            return False
        return self.env[model].sudo().browse(res_id).display_name

    @api.model
    def _get_reply_to(self, values):
        """ Return a specific reply_to for the document """
        model = values.get('model', self._context.get('default_model'))
        res_id = values.get('res_id', self._context.get('default_res_id')) or False
        email_from = values.get('email_from')
        message_type = values.get('message_type')
        records = None
        if self.is_thread_message({'model': model, 'res_id': res_id, 'message_type': message_type}):
            records = self.env[model].browse([res_id])
        else:
            records = self.env[model] if model else self.env['mail.thread']
        return records.sudo()._notify_get_reply_to(default=email_from)[res_id]

    @api.model
    def _get_message_id(self, values):
        if values.get('reply_to_force_new', False) is True:
            message_id = tools.generate_tracking_message_id('reply_to')
        elif self.is_thread_message(values):
            message_id = tools.generate_tracking_message_id('%(res_id)s-%(model)s' % values)
        else:
            message_id = tools.generate_tracking_message_id('private')
        return message_id

    def is_thread_message(self, vals=None):
        if vals:
            res_id = vals.get('res_id')
            model = vals.get('model')
            message_type = vals.get('message_type')
        else:
            self.ensure_one()
            res_id = self.res_id
            model = self.model
            message_type = self.message_type
        return res_id and model and message_type != 'user_notification'

    def _invalidate_documents(self, model=None, res_id=None):
        """ Invalidate the cache of the documents followed by ``self``. """
        fnames = ['message_ids', 'message_needaction', 'message_needaction_counter']
        self.flush_recordset(['model', 'res_id'])
        for record in self:
            model = model or record.model
            res_id = res_id or record.res_id
            if model in self.pool and issubclass(self.pool[model], self.pool['mail.thread']):
                self.env[model].browse(res_id).invalidate_recordset(fnames)

    def _get_search_domain_share(self):
        return ['&', '&', ('is_internal', '=', False), ('subtype_id', '!=', False), ('subtype_id.internal', '=', False)]
