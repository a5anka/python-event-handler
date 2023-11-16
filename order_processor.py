import os
import time
import threading
from random import randint, choice
import logging

# Event class
class Event:
    def __init__(self, event_type, data):
        self.type = event_type
        self.data = data

# A simple mock external service
class MockExternalService:
    def get_event(self):
        # Randomly decide whether to generate an event
        if randint(0, 1):
            event_type = choice(['NewOrder', 'UpdateOrder', 'DeleteOrder'])
            event_data = {'order_id': randint(100, 999)}
            return Event(event_type, event_data)
        return None

# Event handler class
class EventHandler(threading.Thread):
    def __init__(self, external_service):
        super().__init__()
        self.handlers = {}
        self.service = external_service
        self.daemon = True  # Allow the program to exit even if the thread is running

    def register_handler(self, event_type, handler):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def run(self):
        polling_interval = int(os.getenv('POLLING_INTERVAL', 1))  # Default to 1 second if not set
        logging.info(f"Polling interval set to {polling_interval} seconds.")
        while True:
            event = self.service.get_event()
            if event:
                self.dispatch(event)
            time.sleep(polling_interval)  # Polling interval

    def dispatch(self, event):
        if event.type in self.handlers:
            for handler in self.handlers[event.type]:
                handler(event.data)

# Handler functions for different event types
def handle_new_order(order_data):
    print(f"Handling new order: {order_data['order_id']}")

def handle_update_order(order_data):
    print(f"Handling update to order: {order_data['order_id']}")

def handle_delete_order(order_data):
    print(f"Handling deletion of order: {order_data['order_id']}")

# Setup and run the event handler
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    service = MockExternalService()
    event_handler = EventHandler(service)

    # Register event handlers
    event_handler.register_handler('NewOrder', handle_new_order)
    event_handler.register_handler('UpdateOrder', handle_update_order)
    event_handler.register_handler('DeleteOrder', handle_delete_order)

    # Start the event handler thread
    event_handler.start()

    try:
        # Keep the main thread alive
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping the event handler.")
        # You can add any cleanup code here before the application stops.
