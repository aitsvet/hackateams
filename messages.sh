#!/bin/bash

jq '[
  .. | objects | select(.id == 2580880046) | .messages
  | .[]?
  | select(.reply_to_message_id == 2)
  | {
      id,
      date,
      date_unixtime,
      from,
      from_id,
      text: [ .text_entities[].text ] | join(" "),
      reactions: [ (.reactions // [])[]?.recent[]?.from_id ]
    }
]' '~/Загрузки/Telegram Desktop/DataExport_2025-08-09/result.json'