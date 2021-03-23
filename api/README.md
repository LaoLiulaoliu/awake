### Example

1. Here is an example when subscribe channel: 
['spot/account:BSV', 'spot/account:USDT','spot/order:BSV-USDT']
The buy order states' changing 0 0 0 1 2, sell order states' changing 0 0 2

```
order:  [{'client_oid': '', 'created_at': '2021-03-23T09:16:49.254Z', 'event_code': '0', 'event_message': '', 'fee': '', 'fee_currency': '', 'filled_notional': '0', 'filled_size': '0', 'instrument_id': 'BSV-USDT', 'last_amend_result': '', 'last_fill_id': '0', 'last_fill_px': '0', 'last_fill_qty': '0', 'last_fill_time': '1970-01-01T00:00:00.000Z', 'last_request_id': '', 'margin_trading': '1', 'notional': '', 'order_id': '6668616286503936', 'order_type': '0', 'price': '221.66', 'rebate': '', 'rebate_currency': '', 'side': 'buy', 'size': '1', 'state': '0', 'status': 'open', 'timestamp': '2021-03-23T09:16:49.254Z', 'type': 'limit'}]

account:  [{'available': '699.0424765902344', 'balance': '1270.7027689902344', 'currency': 'USDT', 'hold': '571.6602924', 'id': '', 'timestamp': '2021-03-23T09:16:49.254Z'}]
account:  [{'available': '698.5324765902344', 'balance': '1270.7027689902344', 'currency': 'USDT', 'hold': '572.1702924', 'id': '', 'timestamp': '2021-03-23T09:17:15.017Z'}]


order:  [{'client_oid': '', 'created_at': '2021-03-23T09:16:49.254Z', 'event_code': '0', 'event_message': '', 'fee': '', 'fee_currency': '', 'filled_notional': '0', 'filled_size': '0', 'instrument_id': 'BSV-USDT', 'last_amend_result': '0', 'last_fill_id': '0', 'last_fill_px': '0', 'last_fill_qty': '0', 'last_fill_time': '1970-01-01T00:00:00.000Z', 'last_request_id': '', 'margin_trading': '1', 'notional': '', 'order_id': '6668616286503936', 'order_type': '0', 'price': '222.17', 'rebate': '', 'rebate_currency': '', 'side': 'buy', 'size': '1', 'state': '0', 'status': 'open', 'timestamp': '2021-03-23T09:17:15.022Z', 'type': 'limit'}]


account:  [{'available': '698.5324765902344', 'balance': '1270.7027689902344', 'currency': 'USDT', 'hold': '572.1702924', 'id': '', 'timestamp': '2021-03-23T09:17:15.025Z'}]
account:  [{'available': '698.4024765902344', 'balance': '1270.7027689902344', 'currency': 'USDT', 'hold': '572.3002924', 'id': '', 'timestamp': '2021-03-23T09:17:24.879Z'}]
account:  [{'available': '698.4024765902344', 'balance': '1270.7027689902344', 'currency': 'USDT', 'hold': '572.3002924', 'id': '', 'timestamp': '2021-03-23T09:17:24.885Z'}]

order:  [{'client_oid': '', 'created_at': '2021-03-23T09:16:49.254Z', 'event_code': '0', 'event_message': '', 'fee': '', 'fee_currency': '', 'filled_notional': '0', 'filled_size': '0', 'instrument_id': 'BSV-USDT', 'last_amend_result': '0', 'last_fill_id': '0', 'last_fill_px': '0', 'last_fill_qty': '0', 'last_fill_time': '1970-01-01T00:00:00.000Z', 'last_request_id': '', 'margin_trading': '1', 'notional': '', 'order_id': '6668616286503936', 'order_type': '0', 'price': '222.3', 'rebate': '', 'rebate_currency': '', 'side': 'buy', 'size': '1', 'state': '0', 'status': 'open', 'timestamp': '2021-03-23T09:17:24.884Z', 'type': 'limit'}]


account:  [{'available': '698.4114645902344', 'balance': '1204.1106769902344', 'currency': 'USDT', 'hold': '505.6992124', 'id': '', 'timestamp': '2021-03-23T09:17:24.885Z'}]
account:  [{'available': '0.2993004', 'balance': '0.2993004', 'currency': 'BSV', 'hold': '0', 'id': '', 'timestamp': '2021-03-23T09:17:24.885Z'}]

order:  [{'client_oid': '', 'created_at': '2021-03-23T09:16:49.254Z', 'event_code': '0', 'event_message': '', 'fee': '-0.0002996', 'fee_currency': 'BSV', 'filled_notional': '66.592092', 'filled_size': '0.2996', 'instrument_id': 'BSV-USDT', 'last_amend_result': '', 'last_fill_id': '39653498', 'last_fill_px': '222.27', 'last_fill_qty': '0.2996', 'last_fill_time': '2021-03-23T09:17:24.884Z', 'last_request_id': '', 'margin_trading': '1', 'notional': '', 'order_id': '6668616286503936', 'order_type': '0', 'price': '222.3', 'rebate': '', 'rebate_currency': '', 'side': 'buy', 'size': '1', 'state': '1', 'status': 'part_filled', 'timestamp': '2021-03-23T09:17:24.884Z', 'type': 'limit'}]

account:  [{'available': '0.999', 'balance': '0.999', 'currency': 'BSV', 'hold': '0', 'id': '', 'timestamp': '2021-03-23T09:17:24.885Z'}]
account:  [{'available': '698.4324765902344', 'balance': '1048.4327689902344', 'currency': 'USDT', 'hold': '350.0002924', 'id': '', 'timestamp': '2021-03-23T09:17:24.885Z'}]

order:  [{'client_oid': '', 'created_at': '2021-03-23T09:16:49.254Z', 'event_code': '0', 'event_message': '', 'fee': '-0.001', 'fee_currency': 'BSV', 'filled_notional': '222.27', 'filled_size': '1', 'instrument_id': 'BSV-USDT', 'last_amend_result': '', 'last_fill_id': '39653499', 'last_fill_px': '222.27', 'last_fill_qty': '0.7004', 'last_fill_time': '2021-03-23T09:17:24.884Z', 'last_request_id': '', 'margin_trading': '1', 'notional': '', 'order_id': '6668616286503936', 'order_type': '0', 'price': '222.3', 'rebate': '', 'rebate_currency': '', 'side': 'buy', 'size': '1', 'state': '2', 'status': 'filled', 'timestamp': '2021-03-23T09:17:24.884Z', 'type': 'limit'}]

order:  [{'client_oid': '', 'created_at': '2021-03-23T09:17:33.362Z', 'event_code': '0', 'event_message': '', 'fee': '', 'fee_currency': '', 'filled_notional': '0', 'filled_size': '0', 'instrument_id': 'BSV-USDT', 'last_amend_result': '', 'last_fill_id': '0', 'last_fill_px': '0', 'last_fill_qty': '0', 'last_fill_time': '1970-01-01T00:00:00.000Z', 'last_request_id': '', 'margin_trading': '1', 'notional': '', 'order_id': '6668619177162752', 'order_type': '0', 'price': '223', 'rebate': '', 'rebate_currency': '', 'side': 'sell', 'size': '0.999', 'state': '0', 'status': 'open', 'timestamp': '2021-03-23T09:17:33.362Z', 'type': 'limit'}]

account:  [{'available': '0', 'balance': '0.999', 'currency': 'BSV', 'hold': '0.999', 'id': '', 'timestamp': '2021-03-23T09:17:33.362Z'}]
account:  [{'available': '0', 'balance': '0.999', 'currency': 'BSV', 'hold': '0.999', 'id': '', 'timestamp': '2021-03-23T09:19:10.858Z'}]

order:  [{'client_oid': '', 'created_at': '2021-03-23T09:17:33.362Z', 'event_code': '0', 'event_message': '', 'fee': '', 'fee_currency': '', 'filled_notional': '0', 'filled_size': '0', 'instrument_id': 'BSV-USDT', 'last_amend_result': '0', 'last_fill_id': '0', 'last_fill_px': '0', 'last_fill_qty': '0', 'last_fill_time': '1970-01-01T00:00:00.000Z', 'last_request_id': '', 'margin_trading': '1', 'notional': '', 'order_id': '6668619177162752', 'order_type': '0', 'price': '222.6', 'rebate': '', 'rebate_currency': '', 'side': 'sell', 'size': '0.999', 'state': '0', 'status': 'open', 'timestamp': '2021-03-23T09:19:10.864Z', 'type': 'limit'}]

account:  [{'available': '0', 'balance': '0.999', 'currency': 'BSV', 'hold': '0.999', 'id': '', 'timestamp': '2021-03-23T09:19:10.865Z'}]
account:  [{'available': '0', 'balance': '0', 'currency': 'BSV', 'hold': '0', 'id': '', 'timestamp': '2021-03-23T09:19:16.987Z'}]

order:  [{'client_oid': '', 'created_at': '2021-03-23T09:17:33.362Z', 'event_code': '0', 'event_message': '', 'fee': '-0.17790192', 'fee_currency': 'USDT', 'filled_notional': '222.3774', 'filled_size': '0.999', 'instrument_id': 'BSV-USDT', 'last_amend_result': '', 'last_fill_id': '39653757', 'last_fill_px': '222.6', 'last_fill_qty': '0.999', 'last_fill_time': '2021-03-23T09:19:16.986Z', 'last_request_id': '', 'margin_trading': '1', 'notional': '', 'order_id': '6668619177162752', 'order_type': '0', 'price': '222.6', 'rebate': '', 'rebate_currency': '', 'side': 'sell', 'size': '0.999', 'state': '2', 'status': 'filled', 'timestamp': '2021-03-23T09:19:16.986Z', 'type': 'limit'}]
account:  [{'available': '920.6319746702344', 'balance': '1270.6322670702344', 'currency': 'USDT', 'hold': '350.0002924', 'id': '', 'timestamp': '2021-03-23T09:19:16.987Z'}]
```