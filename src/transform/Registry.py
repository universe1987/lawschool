from Student import Student
from School import School
from Application import Application



def is_peer(student1, student2):
    LSAT_radius = 0.5
    GPA_radius = 0.03
    LSAT_diff = abs(student1.LSAT - student2.LSAT)
    GPA_diff = abs(student1.GPA - student2.GPA) 
    if (LSAT_diff <= LSAT_radius) & (GPA_diff <= GPA_radius) :
        return True
    else:
        return False
    

class Registry:
    def __init__(self):
        self.students = {}
        self.schools = {}
        self.applications = {}
        #self.peers = {}
        #self.peer_names = {}
    
    ''' # Redundant Codes
    def get_or_create_one_peer_name(self,own_name,peer_name):
        if own_name in self.peer_names:
            if peer_name in self.peer_names[own_name]:
                return
            else:
                self.peer_names[own_name].append(peer_name)
        else:
            self.peer_names[own_name] = []
            if peer_name!='':
                self.peer_names[own_name].append(peer_name)
        return
        
    def get_or_create_one_peer(self,own_name,peer_name):
        if own_name in self.peers:
            if peer_name in self.peers[own_name]:
                return 
            else:
                peer = self.get_or_create_student(peer_name,0.0,0.0)
                self.peers[own_name][peer_name] = peer
        else:
            self.peers[own_name] = {}
            if peer_name!='':
                peer = self.get_or_create_student(peer_name,0.0,0.0)
                self.peers[own_name][peer_name] = peer

    
    def get_all_peer_names(self,own_name):
        return self.peer_names[own_name] 
    
    def get_all_peers(self,own_name):
        return self.peers[own_name] 
    '''

    def get_or_create_student(self, name, LSAT, GPA):
        if name in self.students:
            return self.students[name]
        else:
            current_student = Student(name)
            current_student.LSAT = LSAT
            current_student.GPA = GPA
            for existing_student in self.students.itervalues():
                if is_peer(current_student, existing_student):
                    current_student.add_peer(existing_student)
                    existing_student.add_peer(current_student)
            self.students[name] = current_student
            return current_student

    def get_or_create_school(self, name):
        if name in self.schools:
            return self.schools[name]
        else:
            school = School(name)
            self.schools[name] = school
            return school

    def create_application(self, student, school, time):
        key = (student.name, school.name)
        assert key not in self.applications, key
        application = Application(student, school, time)
        self.applications[key] = application
        return application

    def get_application(self, student, school):
        key = (student.name, school.name)
        return self.applications.get(key, None)

    def get_applicant_info(self, student):
        print('{} has {} offers, {} waiting lists, {} rejections'.format(student.name, len(student.offers),
                                                                         len(student.waiting_list),
                                                                         len(student.rejections)))
    def get_school_info(self,school):
        print('{} has received {} applications, sent {} offers, {} waiting lists, {} rejections'.format(school.name, 
                                                                         len(school.applications),
                                                                         len(school.offers),
                                                                         len(school.waiting_list),
                                                                         len(school.rejections)))
        