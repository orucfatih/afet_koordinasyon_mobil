class PersonnelStateManager:
    _instance = None
    _current_team = None
    _debug = True  # Debug için

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PersonnelStateManager()
        return cls._instance

    @classmethod
    def set_current_team(cls, team_id):
        cls._current_team = team_id
        if cls._debug:
            print(f"Current team set to: {team_id}")

    @classmethod
    def get_current_team(cls):
        if cls._debug:
            print(f"Current team is: {cls._current_team}")
        return cls._current_team