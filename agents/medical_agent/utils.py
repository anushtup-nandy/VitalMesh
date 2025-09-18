import os
import yaml
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

def load_prompt(filename: str) -> str:
    """Load a prompt from a YAML file in the prompts directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(script_dir, 'prompts', filename)
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as file:
            prompt_data = yaml.safe_load(file)
            return prompt_data.get('instructions', '')
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Warning: Error loading prompt file {filename}: {e}")
        return f"You are a helpful medical assistant. Please assist the patient professionally."

def save_patient_notes(notes_data: Dict[str, Any], patient_identifier: Optional[str] = None) -> str:
    """
    Save patient notes to the patient_data folder.
    
    Args:
        notes_data: Dictionary containing patient session data
        patient_identifier: Optional patient name/ID for filename
        
    Returns:
        str: Filename of saved notes
    """
    # Create patient_data directory if it doesn't exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    patient_data_dir = os.path.join(script_dir, 'patient_data')
    Path(patient_data_dir).mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    patient_id = patient_identifier or "unknown_patient"
    
    # Clean patient identifier for filename (remove invalid filename characters)
    clean_patient_id = "".join(c for c in patient_id if c.isalnum() or c in (' ', '-', '_')).rstrip()
    clean_patient_id = clean_patient_id.replace(' ', '_')
    
    filename = f"{clean_patient_id}_{timestamp}_notes.yaml"
    filepath = os.path.join(patient_data_dir, filename)
    
    try:
        # Add metadata to notes
        enriched_notes = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "patient_identifier": patient_identifier,
                "system_version": "1.0",
                "file_type": "medical_session_notes"
            },
            "session_data": notes_data
        }
        
        # Save as YAML for better readability
        with open(filepath, 'w', encoding='utf-8') as file:
            yaml.dump(enriched_notes, file, default_flow_style=False, indent=2, allow_unicode=True)
        
        print(f"Patient notes saved to: {filepath}")
        return filename
        
    except Exception as e:
        print(f"Error saving patient notes as YAML: {e}")
        # Fallback to JSON if YAML fails
        json_filename = f"{clean_patient_id}_{timestamp}_notes.json"
        json_filepath = os.path.join(patient_data_dir, json_filename)
        
        try:
            with open(json_filepath, 'w', encoding='utf-8') as file:
                json.dump(enriched_notes, file, indent=2, default=str, ensure_ascii=False)
            print(f"Patient notes saved as JSON to: {json_filepath}")
            return json_filename
        except Exception as json_error:
            print(f"Error saving as JSON: {json_error}")
            raise e

def list_patient_notes() -> List[Dict[str, Any]]:
    """
    List all patient notes files in the patient_data directory.
    
    Returns:
        List of dictionaries containing file information
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    patient_data_dir = os.path.join(script_dir, 'patient_data')
    
    if not os.path.exists(patient_data_dir):
        return []
    
    notes_files = []
    for filename in os.listdir(patient_data_dir):
        if filename.endswith(('_notes.yaml', '_notes.json')):
            filepath = os.path.join(patient_data_dir, filename)
            try:
                stat = os.stat(filepath)
                notes_files.append({
                    'filename': filename,
                    'path': filepath,
                    'created': datetime.fromtimestamp(stat.st_ctime),
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'size': stat.st_size
                })
            except OSError as e:
                print(f"Warning: Could not read file stats for {filename}: {e}")
    
    return sorted(notes_files, key=lambda x: x['created'], reverse=True)

def load_patient_notes(filename: str) -> Optional[Dict[str, Any]]:
    """
    Load patient notes from a file.
    
    Args:
        filename: Name of the notes file to load
        
    Returns:
        Dictionary containing patient notes or None if error
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    patient_data_dir = os.path.join(script_dir, 'patient_data')
    filepath = os.path.join(patient_data_dir, filename)
    
    try:
        if filename.endswith('.yaml'):
            with open(filepath, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        elif filename.endswith('.json'):
            with open(filepath, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            raise ValueError(f"Unsupported file format: {filename}")
            
    except Exception as e:
        print(f"Error loading patient notes from {filename}: {e}")
        return None

def search_patient_notes(search_term: str) -> List[Dict[str, Any]]:
    """
    Search for patient notes containing a specific term.
    
    Args:
        search_term: Term to search for in patient notes
        
    Returns:
        List of matching notes with excerpts
    """
    search_term_lower = search_term.lower()
    matching_notes = []
    
    for note_info in list_patient_notes():
        notes_data = load_patient_notes(note_info['filename'])
        if notes_data:
            # Convert notes to string for searching
            notes_str = json.dumps(notes_data, default=str).lower()
            if search_term_lower in notes_str:
                matching_notes.append({
                    'filename': note_info['filename'],
                    'created': note_info['created'],
                    'notes_data': notes_data
                })
    
    return matching_notes

def get_patient_summary(patient_identifier: str) -> Optional[Dict[str, Any]]:
    """
    Get a summary of all notes for a specific patient.
    
    Args:
        patient_identifier: Patient name or ID
        
    Returns:
        Summary dictionary or None if no notes found
    """
    patient_notes = []
    
    for note_info in list_patient_notes():
        if patient_identifier.lower() in note_info['filename'].lower():
            notes_data = load_patient_notes(note_info['filename'])
            if notes_data:
                patient_notes.append({
                    'date': note_info['created'],
                    'data': notes_data
                })
    
    if not patient_notes:
        return None
    
    # Create summary
    summary = {
        'patient_identifier': patient_identifier,
        'total_sessions': len(patient_notes),
        'date_range': {
            'first_visit': min(note['date'] for note in patient_notes),
            'last_visit': max(note['date'] for note in patient_notes)
        },
        'sessions': patient_notes
    }
    
    return summary

def create_directory_structure():
    """
    Create the required directory structure for the medical agent system.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    directories = [
        'patient_data',
        'prompts',
        'logs'
    ]
    
    for directory in directories:
        dir_path = os.path.join(script_dir, directory)
        Path(dir_path).mkdir(exist_ok=True)
        print(f"Created directory: {dir_path}")

def validate_patient_data(notes_data: Dict[str, Any]) -> List[str]:
    """
    Validate patient notes data for completeness.
    
    Args:
        notes_data: Patient session data to validate
        
    Returns:
        List of validation warnings/errors
    """
    warnings = []
    
    required_fields = ['patient_name', 'session_start']
    for field in required_fields:
        if not notes_data.get(field):
            warnings.append(f"Missing required field: {field}")
    
    # Check for empty notes
    if not notes_data.get('notes') or len(notes_data.get('notes', [])) == 0:
        warnings.append("No session notes recorded")
    
    # Check for missing complaint/symptoms
    if not notes_data.get('chief_complaint') and not notes_data.get('symptoms'):
        warnings.append("No chief complaint or symptoms recorded")
    
    return warnings

def export_notes_to_csv(output_filename: str = None) -> str:
    """
    Export all patient notes to a CSV file for analysis.
    
    Args:
        output_filename: Optional filename for export
        
    Returns:
        Path to exported CSV file
    """
    import csv
    
    if not output_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"patient_notes_export_{timestamp}.csv"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'patient_data', output_filename)
    
    all_notes = []
    for note_info in list_patient_notes():
        notes_data = load_patient_notes(note_info['filename'])
        if notes_data and 'session_data' in notes_data:
            session = notes_data['session_data']
            all_notes.append({
                'filename': note_info['filename'],
                'patient_name': session.get('patient_name', ''),
                'session_date': session.get('session_start', ''),
                'chief_complaint': session.get('chief_complaint', ''),
                'symptoms': ', '.join(session.get('symptoms', [])),
                'appointment_type': session.get('appointment_type', ''),
                'insurance_info': session.get('insurance_info', ''),
                'notes_count': len(session.get('notes', [])),
                'current_agent': session.get('current_agent', '')
            })
    
    # Write to CSV
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            if all_notes:
                fieldnames = all_notes[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_notes)
            
        print(f"Notes exported to: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        raise e

def cleanup_old_notes(days_old: int = 30) -> int:
    """
    Remove patient notes older than specified days.
    
    Args:
        days_old: Number of days after which to remove notes
        
    Returns:
        Number of files removed
    """
    cutoff_date = datetime.now() - timedelta(days=days_old)
    removed_count = 0
    
    for note_info in list_patient_notes():
        if note_info['created'] < cutoff_date:
            try:
                os.remove(note_info['path'])
                print(f"Removed old notes file: {note_info['filename']}")
                removed_count += 1
            except OSError as e:
                print(f"Error removing {note_info['filename']}: {e}")
    
    return removed_count