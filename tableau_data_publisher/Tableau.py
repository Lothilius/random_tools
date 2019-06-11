__author__ = 'Lothilius'
# coding: utf-8

import json
import requests
from bv_authenticate.Authentication import Authentication as creds
import pandas as pd
import tableauserverclient as TSC

pd.set_option('display.width', 260)


class Tableau(object):
    """ Tableau connector that helps create the tableau connection to a Tableau server for publishing and gathering
    server information.
    """
    def __init__(self, server_url='', site_id='', project=''):
        url, user_name, password = creds.tableau_publishing()
        if server_url == '':
            self.server_url = url
        else:
            self.server_url = server_url
        self.project = {}
        self.site_id = site_id
        self.tableau_auth = TSC.TableauAuth(user_name, password, site_id=self.site_id)
        self.server = TSC.Server(server_url)
        self.server.auth.sign_in(self.tableau_auth)
        self.project = self.get_project_id(project)

    def get_project_id(self, project_name=''):
        """Given a project name or using the server object with a site_id return either the specific project id or
        return the dictionary of project by name giving their id.
        :param project_name: string that returns it's id
        :return: dictionary if project_name is not given otherwise a string of the id.
        """
        for each in self.server.projects.get()[0]:
            self.project.update({each.name: each.id})
        if project_name == '':
            return self.project
        else:
            try:
                return self.project[project_name]
            except KeyError:
                return self.project
            except:
                print 'Something went wrong'

    def publish_datasource(self, project, file_path, mode, name='', tags=()):
        """ Use this method to help Publish datasources to Tableau server.
        :param project: string
        :param file_path: string with file name included at the end of the path
        :param mode: String of the following options ['CreateNew','Append','Overwrite']
        :param name: Name of the published Datasource will default to file name
        :param tags: Any tags for the Data source.
        :return: Nothing
        """
        if name == '':
            name = file_path.split('/')[-1].split('.')[0]
        testing_datasource = TSC.DatasourceItem(project_id=self.project[project], name=name)
        if tags != ():
            testing_datasource.tags(tags)
        try:
            self.server.datasources.publish(datasource_item=testing_datasource, file_path=file_path, mode=mode)
            print "Published %s to %s in %s" % (name, project, self.site_id)
        except Exception, e:
            # Handle the exception depending on the type of exception received
            error_message = "Error: " + e.args[0]

            raise error_message

    def set_url(self, url):
        self.server_url = url



if __name__ == '__main__':
    tableau_title = Tableau(server_url='https://tableau.bazaarvoice.com/', site_id='BizTech')
    tableau_title.publish_datasource(project='Testing', mode='CreateNew',
                                     file_path='/Users/martin.valenzuela/Downloads/BizApps_HDT_.hyper')
