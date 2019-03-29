class Application:
    PENDING = 'pending'
    OFFER = 'offer'
    WAITING_LIST = 'waiting_list'
    REJECTION = 'rejection'

    def __init__(self, student, school, time):
        self.student = student
        self.school = school
        self.application_time = time
        self.decision = self.PENDING
        self.decision_time = None
        self.application_weekday = None
        self.round = 1

    def send_application(self):
        self.student.application_sent(self)
        self.school.application_received(self)
        self.round = len(self.student.applications_per_day) - self.student.applications_per_day.count([])


    def send_decision(self, decision, time):
        if decision == self.OFFER:
            assert self.decision == self.PENDING or self.decision == self.WAITING_LIST
        elif decision == self.WAITING_LIST:
            assert self.decision == self.PENDING
        elif decision == self.REJECTION:
            assert self.decision == self.PENDING or self.decision == self.WAITING_LIST
        else:
            assert False, 'Invalid decision ' + decision
        self.decision = decision
        self.decision_time = time
        self.school.decision_sent(self)
        self.student.decision_received(self)


    def is_offer(self):
        return self.decision == self.OFFER

    def is_waiting_list(self):
        return self.decision == self.WAITING_LIST

    def is_rejection(self):
        return self.decision == self.REJECTION
