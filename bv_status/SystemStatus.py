__author__ = 'Lothilius'

from SFDC import SFDC
from Helpdesk import Helpdesk
from Concur import Concur
from Netsuite import Netsuite

class SystemStatus(object):
    # Initiate the status list
    def __init__(self):
        """ Create an empty System status list.
        :return: list
        """
        self.system_list = dict({'Helpdesk': Helpdesk().__dict__,
                                 'Salesforce': SFDC().__dict__,
                             'Netsuite': Netsuite().__dict__,
                             'Concur': Concur().__dict__})


    def refresh_system_status(self):
        self.__init__()
        # TODO - break out the refresh to individual system calls. First try below.
        # if system.capitalize() in self.system_list.keys():
        #     if system.capitalize() == 'Salesforce':
        #         self.system_list[system.capitalize()] = SFDC().__dict__
        #     else:
        #         system_initialize = eval(system.capitalize())
        #         self.system_list[system.capitalize()] = system_initialize.__dict__

if __name__ == "__main__":
    system = SystemStatus()
    print str(system.system_list)
    system.refresh_system_status()
    print str(system.system_list)