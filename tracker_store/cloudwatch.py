from typing import (
    Any,
    Dict,
    Optional,
    Text
)

import boto3
from datetime import datetime
import json

from rasa.core.tracker_store import TrackerStore
from rasa.shared.core.domain import Domain
from rasa.shared.core.trackers import DialogueStateTracker
from rasa.utils.endpoints import EndpointConfig


class CloudwatchTrackerStore(TrackerStore):
    """
    Stores conversation history in Cloudwatch
    """
    def __init__(
            self,
            domain: Domain,
            log_group_name: Text = "chat-history",
            region: Text = "us-east-1",
            event_broker: Optional[EndpointConfig] = None,
            **kwargs: Dict[Text, Any],
    ) -> None:
        """Initialize `CloudwatchTrackerStore`.
        Args:
            domain: Domain associated with this tracker store.
            log_group_name: The name of the log group where log stream will be stored in cloudwatch
            region: The name of the region associated with the client. A client is associated with a single region.
            event_broker: An event broker used to publish events.
            kwargs: Additional kwargs.
        """
        # print("hello")
        self.client = boto3.client("logs", region_name=region)
        self.region = region
        self.log_group_name = log_group_name
        super().__init__(domain, event_broker, **kwargs)

    def create_log_stream_name(self, log_stream_name):
        """
        creates new log stream
        """
        response = self.client.create_log_stream(
            logGroupName=self.log_group_name,
            logStreamName=log_stream_name,
        )
        # print(response)
        return response

    def get_sequence_token(self, log_stream_name):
        """
        get sequence token number if the log stream is already created and data is stored inside it once
        """
        response = self.client.describe_log_streams(
            logGroupName=self.log_group_name,
            logStreamNamePrefix=log_stream_name
        )
        # print(response)
        return response

    def save(self, tracker: DialogueStateTracker) -> None:
        """Saves the current conversation state."""
        if self.event_broker:
            self.stream_events(tracker)
        serialized = self.serialise_tracker(tracker)

        sender = tracker.sender_id
        # split_sender = sender.split("_")
        # userid = split_sender[0]
        # senderid = split_sender[1]
        # log_stream_name = userid + "/" + senderid
        log_stream_name = sender
        current_datetime = datetime.now()
        timestamp = int(datetime.timestamp(current_datetime))
        sequence_token = self.get_sequence_token(log_stream_name)
        check_sequence_token_response = sequence_token['logStreams']
        # if log_stream_name already exists in log_group_name
        if len(check_sequence_token_response) != 0:
            sequence_token_number = sequence_token['logStreams'][0]['uploadSequenceToken']
            response = self.client.put_log_events(
                logGroupName=self.log_group_name,
                logStreamName=log_stream_name,
                logEvents=[
                    {
                        'timestamp': timestamp * 1000,  # must be in millisecond
                        'message': json.dumps(serialized)
                    },
                ],
                sequenceToken=sequence_token_number
            )
            # print(response)
            return None
        # if log_stream_name doesn't exist in log_group_name, then first it creates it
        else:
            val = self.create_log_stream_name(log_stream_name)
            response = self.client.put_log_events(
                logGroupName=self.log_group_name,
                logStreamName=log_stream_name,
                logEvents=[
                    {
                        'timestamp': timestamp * 1000,  # must be in millisecond
                        'message': json.dumps(serialized)
                    },
                ],
            )
            # print(response)
            return None

    def serialise_tracker(self, tracker: "DialogueStateTracker") -> Dict:
        """Serializes the tracker, returns object with decimal types."""
        dialogue = tracker.as_dialogue().as_dict()
        return dialogue

    def retrieve(self, sender_id: Text) -> Optional[DialogueStateTracker]:
        # Retrieve dialogues for a sender_id in reverse-chronological order based on
        # the session_date sort key
        sender = sender_id
        # split_sender = sender.split("_")
        # userid = split_sender[0]
        # senderid = split_sender[1]
        # log_stream_name = userid + "/" + senderid
        log_stream_name = sender
        # response = self.client.describe_log_streams(
        #     logGroupName=self.log_group_name,
        #     logStreamNamePrefix=log_stream_name,
        #     orderBy='LogStreamName',
        #     descending=True,
        # )
        # result = response['logStreams']
        try:
            log_events_response = self.client.get_log_events(
                logGroupName=self.log_group_name,
                logStreamName=log_stream_name,
            )
            log_events_result = log_events_response['events'][::-1]
            stored_txt = log_events_result[0]['message']
            stored = json.loads(stored_txt)
            stored_events = stored['events']
            dialogue_state = DialogueStateTracker.from_dict(sender_id, stored_events, self.domain.slots)
            return dialogue_state
        except Exception as e:
            return None

    # def keys(self) -> Iterable[Text]:
        # """Returns sender_ids"""
        # return [
        #     i["sender_id"]
        #     for i in self.db.scan(ProjectionExpression="sender_id")["Items"]
        # ]
