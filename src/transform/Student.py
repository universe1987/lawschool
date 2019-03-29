import numpy as np

class Student:
    ALL_DAY = 366
    
    def __init__(self, name):
        self.name = name
        self.GPA = 0.0
        self.LSAT = 0.0
        self.applications = []
        self.offers = {}
        self.waiting_list = {}
        self.rejections = {}
        self.applications_per_day = [[] for i in range(self.ALL_DAY+1)]
        self.offers_per_day = [{} for i in range(self.ALL_DAY+1)] # Number of Apps sent on Day X converted to offers eventually
        self.rejections_per_day = [{} for i in range(self.ALL_DAY+1)]
        self.waiting_list_per_day = [{} for i in range(self.ALL_DAY+1)]
        self.applicant_type = '' #Once,Multiple,Updates
        self.total_rounds = 0
        self.ranked_only = 1 # Send apps only to ranked schools
        self.peers = []
        self.peer_offers = []
        self.peer_rejections = []
        self.peer_waitlists = []
        self.applicant_peer_type = ''#Once,Multiple,Updates
        self.offers_received_per_day = [{} for i in range(self.ALL_DAY+1)] # Number of Offers Received on Day X
        self.rejections_received_per_day = [{} for i in range(self.ALL_DAY+1)] # Number of Offers Received on Day X
        self.peer_offers_received_per_day = [[] for i in range(self.ALL_DAY+1)]
        self.peer_rejections_received_per_day = [[] for i in range(self.ALL_DAY+1)]
        self.round_dates = [] #when sending rounds

    def add_peer(self, peer):
        self.peers.append(peer)
        
    def application_sent(self, application):
        t_lag = self.applications[-1].application_time if self.applications else -1
        self.applications.append(application)
        t = int(application.application_time)
        self.applications_per_day[t].append(application)
        if t not in self.round_dates:
            self.round_dates.append(t)
        
        self.total_rounds = self.total_rounds + (t>t_lag)
        if self.total_rounds==1:
            self.applicant_type = 'Group 1'
        elif len(self.offers)+len(self.waiting_list)+len(self.rejections)==0:
            self.applicant_type = 'Group 2'
        else:
            self.applicant_type = 'Group 3'
            
        if self.total_rounds==1:
            self.applicant_peer_type = 'Group 1'
        elif len(self.peer_offers)+len(self.peer_waiting_list)+len(self.peer_rejections)==0:
            self.applicant_peer_type = 'Group 2'
        else:
            self.applicant_peer_type = 'Group 3'
            
        if (self.ranked_only==0) or (application.school.ranked==0):
            self.ranked_only = 0
            
    def decision_received(self, application):
        school_name = application.school.name
        t1 = int(application.decision_time)
        t0 = int(application.application_time)
        if application.is_offer():
            self.offers[school_name] = application
            self.offers_per_day[t0][school_name] = application
            self.offers_received_per_day[t1][school_name] = application
            if school_name in self.waiting_list:
                del self.waiting_list[school_name]
                del self.waiting_list_per_day[t0][school_name]
        elif application.is_waiting_list():
            self.waiting_list[school_name] = application
            self.waiting_list_per_day[t0][school_name] = application
        elif application.is_rejection():
            self.rejections[school_name] = application
            self.rejections_per_day[t0][school_name] = application
            self.rejections_received_per_day[t1][school_name] = application
            if school_name in self.waiting_list:
                del self.waiting_list[school_name]
                del self.waiting_list_per_day[t0][school_name]
