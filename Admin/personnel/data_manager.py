class PersonnelDataManager:
    def __init__(self):
        self.ekipler = {}
    
    def add_personnel(self, team_name, personnel_data):
        if team_name not in self.ekipler:
            self.ekipler[team_name] = {"personnel": []}
        self.ekipler[team_name]["personnel"].append(personnel_data)
    
    def update_personnel(self, team_name, old_data, new_data):
        team = self.ekipler.get(team_name)
        if team:
            for i, person in enumerate(team["personnel"]):
                if person == old_data:
                    team["personnel"][i] = new_data
                    break
    
    def get_team_personnel(self, team_name):
        return self.ekipler.get(team_name, {}).get("personnel", []) 