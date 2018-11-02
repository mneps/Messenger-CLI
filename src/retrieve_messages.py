import fbchat.models
import fbchat.graphql
import fbchat.utils
import emoji_class


class Receive(object):

    def __init__(self, fb_client):
            self.fb_client = fb_client
            emoji_test.extend_emojis()


    def fetchThreadMessages(self, thread_id, limit):
        """
        Get the last messages in a thread

        :param thread_id: User/Group ID to get messages from. See :ref:`intro_threads`
        :param limit: Max. number of messages to retrieve
        :param before: A timestamp, indicating from which point to retrieve messages
        :type limit: int
        :type before: int
        :return: :class:`models.Message` objects
        :rtype: list
        :raises: FBchatException if request failed
        """

        thread_id, thread_type = self.fb_client._getThread(thread_id, None)

        j = self.fb_client.graphql_request(fbchat.graphql.GraphQL(doc_id='1386147188135407', params={
            'id': thread_id,
            'message_limit': limit,
            'load_messages': True,
            'load_read_receipts': True,
        }))

        if j.get('message_thread') is None:
            raise fbchat.models.FBchatException('Could not fetch thread {}: {}'.format(thread_id, j))

        messages = list(reversed([self.graphql_to_message(message) for message in j['message_thread']['messages']['nodes']]))

        return messages


    def graphql_to_message(self, message):
        if message.get('message_sender') is None:
            message['message_sender'] = {}
        if message.get('message') is None:
            message['message'] = {}
        rtn = fbchat.models.Message(
            text=message.get('message').get('text'),
            mentions=[fbchat.models.Mention(m.get('entity', {}).get('id'), offset=m.get('offset'), length=m.get('length')) for m in message.get('message').get('ranges', [])],
            emoji_size=fbchat.utils.get_emojisize_from_tags(message.get('tags_list')),
            sticker=fbchat.graphql.graphql_to_sticker(message.get('sticker'))
        )

        rtn.uid = str(message.get('message_id'))
        rtn.author = str(message.get('message_sender').get('id'))
        rtn.timestamp = message.get('timestamp_precise')
        if message.get('unread') is not None:
            rtn.is_read = not message['unread']
        rtn.reactions = {str(r['user']['id']):emoji_test.MessageReaction(r['reaction']) for r in message.get('message_reactions')}
        if message.get('blob_attachments') is not None:
            rtn.attachments = [fbchat.graphql.graphql_to_attachment(attachment) for attachment in message['blob_attachments']]

        return rtn




