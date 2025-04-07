from PyQt5.QtWidgets import QMessageBox, QHeaderView
from sample_data import TEAM_DATA, TASK_DETAILS

class TaskManager:
    @staticmethod
    def check_team_availability(team_name):
        """Check if a team is available for a new task"""
        for team in TEAM_DATA:
            if f"{team[0]} - {team[1]} ({team[2]})" == team_name:
                return team[3] == "Müsait", team[4] if team[3] == "Meşgul" else None
        return True, None  # Default to available if team not found

    @staticmethod
    def update_team_status(team_name, status, team_list=None):
        """Update the status of a team (Müsait/Meşgul)"""
        updated = False
        for i, team in enumerate(TEAM_DATA):
            if f"{team[0]} - {team[1]} ({team[2]})" == team_name:
                team[3] = status
                if status == "Meşgul":
                    team[4] = "Aktif görev var"
                else:
                    team[4] = ""
                updated = True
                
                # If team_list widget is provided, update the table directly
                if team_list:
                    # Update status cell
                    status_item = team_list.item(i, 3)
                    if status_item:
                        status_item.setText(status)
                    
                    # Update contact/notes cell
                    notes_item = team_list.item(i, 4)
                    if notes_item:
                        notes_item.setText(team[4])
                    
                    # Ensure columns maintain their size
                    header = team_list.horizontalHeader()
                    for column in range(header.count()):
                        header.setSectionResizeMode(column, QHeaderView.Stretch)
                break
        return updated

    @staticmethod
    def assign_task(parent, team_name, title, location, priority, task_details, team_list=None):
        """Assign a task to a team with availability check"""
        # Check team availability
        is_available, current_task = TaskManager.check_team_availability(team_name)
        
        if not is_available:
            # Show warning dialog with current task info
            reply = QMessageBox.question(
                parent,
                'Ekip Meşgul',
                f'Seçili ekip şu anda meşgul:\n\n'
                f'Mevcut Görev: {current_task}\n\n'
                f'Yine de yeni görevi atamak istiyor musunuz?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return False

        # Create task text
        task_text = f"{title} - {location} - {priority}"
        
        # Add task details
        TASK_DETAILS[task_text] = (
            f"Ekip: {team_name}\n"
            f"Başlık: {title}\n"
            f"Lokasyon: {location}\n"
            f"Öncelik: {priority}\n"
            f"Detaylar: {task_details}"
        )
        
        # Update team status
        TaskManager.update_team_status(team_name, "Meşgul", team_list)
        
        return True

    @staticmethod
    def complete_task(team_name, team_list=None):
        """Mark a task as complete and update team status"""
        TaskManager.update_team_status(team_name, "Müsait", team_list) 