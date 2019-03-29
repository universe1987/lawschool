import numpy as np

class School:
    ALL_DAY = 366
    def __init__(self, name):
        self.name = name
        self.applications = []
        self.offers = {}
        self.waiting_list = {}
        self.rejections = {}
        self.rank_2010 = np.nan
        self.ranked_2010 = np.nan
        self.rank = np.nan
        self.ranked = np.nan
        self.rank_ic = np.nan
        self.applications_per_day = [[] for i in range(self.ALL_DAY+1)]
        self.offers_per_day = [{} for i in range(self.ALL_DAY+1)]
        self.rejections_per_day = [{} for i in range(self.ALL_DAY+1)]
        self.waiting_list_per_day = [{} for i in range(self.ALL_DAY+1)]
        self.applications_by_day = [[] for i in range(self.ALL_DAY+1)]
        self.offers_by_day = [{} for i in range(self.ALL_DAY+1)]
        self.rejections_by_day = [{} for i in range(self.ALL_DAY+1)]
        self.waiting_list_by_day = [{} for i in range(self.ALL_DAY+1)]

        
    def application_received(self, application):
        self.applications.append(application)
        
        t = int(application.application_time)
        self.applications_per_day[t].append(application)
        for i in range(t, self.ALL_DAY+1):
            self.applications_by_day[i].append(application)
        

    def decision_sent(self, application):
        student_name = application.student.name
        
        t = int(application.decision_time)
        
        if application.is_offer():
            self.offers[student_name] = application
            self.offers_per_day[t][student_name] = application
            for i in range(t, self.ALL_DAY+1):
                self.offers_by_day[i][student_name] = application
            if student_name in self.waiting_list:
                del self.waiting_list[student_name]
                del self.waiting_list_per_day[t][student_name] 
                for i in range(t, self.ALL_DAY+1):
                    del self.waiting_list_by_day[i][student_name]  

        elif application.is_waiting_list():
            self.waiting_list[student_name] = application
            self.waiting_list_per_day[t][student_name] = application
            for i in range(t, self.ALL_DAY+1):
                self.waiting_list_by_day[i][student_name] = application
                
        elif application.is_rejection():
            self.rejections[student_name] = application
            self.rejections_per_day[t][student_name] = application
            for i in range(t, self.ALL_DAY+1):
                self.rejections_by_day[i][student_name] = application
            if student_name in self.waiting_list:
                del self.waiting_list[student_name]
                del self.waiting_list_by_day[t][student_name] 
                for i in range(t, self.ALL_DAY+1):
                    del self.waiting_list_by_day[i][student_name]  


