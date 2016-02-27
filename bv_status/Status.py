class Status(object):

    def __init__(self):
        self.status = 2
        self.status_message = 'Loading Message'
        self.error_message = '?'
        self.tickets = self.get_all_tickets()

    def __str__(self):
        """
        :return: string of all values of class.
        """
        return "{'Status':'%s', 'Status Message':'%s', 'Tickets':'%s', 'Error Message':'%s'}" \
               % (self.status, self.status_message, self.tickets, self.error_message)

    def get_all_tickets(self):
        return -1

    def set_status(self, status_value):
        self.status = status_value

    def set_error_message(self, message):
        self.error_message = message

    def set_status_message(self, message):
        self.status_message = message
