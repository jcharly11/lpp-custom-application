from models.actions_model import actions_model


class actionsController(object):

    def __init__(self):
        pass
    
    def save_action(self, model):
        if model != None:
            model.save_action()
            return True

    def save_action_epc(self, model):
        if model != None:
            model.save()
            return True
            
    def get_all(self):
        return actions_model.get_actions()