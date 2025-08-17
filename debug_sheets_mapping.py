#!/usr/bin/env python3
"""
Script de debug pour analyser le mapping des colonnes Google Sheets
"""

def debug_row_data_construction():
    """Debug de la construction du tableau row_data"""
    
    # Simuler des données de lead typiques
    sample_lead_data = {
        'id': 'test-123',
        'nom': 'TestNom',
        'prénom': 'TestPrénom', 
        'email': 'test@test.com',
        'téléphone': '0123456789',
        'adresse': '123 rue Test',
        'ville': 'Lyon',
        'code_postal': '69001',
        'source': 'manuel',
        'statut': 'nouveau',
        'type_propriete': 'appartement',
        'budget_min': 200000,
        'budget_max': 300000,
        'surface_min': 50,
        'notes_commerciales': 'Test notes',
        'agent_assigne': 'Patrick Almeida',
        'score_qualification': 85,
        'date_creation': '2025-01-17',
        'date_derniere_modification': '2025-01-17',
        'dernière_activité': '2025-01-17'
    }
    
    # Construction du tableau comme dans le code
    row_data = [
        sample_lead_data.get('id', ''),                                # Position 1: ID
        sample_lead_data.get('nom', ''),                               # Position 2: Nom  
        sample_lead_data.get('prénom', ''),                            # Position 3: Prénom
        sample_lead_data.get('email', ''),                             # Position 4: Email
        sample_lead_data.get('téléphone', ''),                         # Position 5: Téléphone
        sample_lead_data.get('adresse', ''),                           # Position 6: Adresse
        sample_lead_data.get('ville', ''),                             # Position 7: Ville
        sample_lead_data.get('code_postal', ''),                       # Position 8: Code Postal
        sample_lead_data.get('source', ''),                            # Position 9: Source
        sample_lead_data.get('statut', ''),                            # Position 10: Statut
        sample_lead_data.get('type_propriete', ''),                    # Position 11: Type
        '',                                                            # Position 12: Propriété (vide)
        str(sample_lead_data.get('budget_min', '')),                   # Position 13: Budget Min
        str(sample_lead_data.get('budget_max', '')),                   # Position 14: Budget Max
        str(sample_lead_data.get('surface_min', '')),                  # Position 15: Surface Min
        sample_lead_data.get('notes_commerciales', ''),                # Position 16: Notes Commerciales
        sample_lead_data.get('agent_assigne', 'Patrick Almeida'),      # Position 17: Agent Assigné ← SHOULD BE HERE!
        str(sample_lead_data.get('score_qualification', '')),          # Position 18: Score Qualité ← SHOULD BE HERE!
        sample_lead_data.get('date_creation'),                         # Position 19: Date Création
        sample_lead_data.get('date_derniere_modification'),            # Position 20: Dernière Modification  
        sample_lead_data.get('dernière_activité')                      # Position 21: Dernière Activité
    ]
    
    print("=== DEBUG ROW DATA CONSTRUCTION ===")
    print(f"Total elements in row_data: {len(row_data)}")
    print()
    
    # Headers attendus dans Google Sheets (structure réelle observée)
    expected_headers = [
        "ID", "Nom", "Prénom", "Email", "Téléphone", 
        "Adresse", "Ville", "Code Postal", "Source", "Statut",
        "Type", "Propriété", "Budget Min", "Budget Max", "Surface Min", 
        "Notes Commerciales", "Agent Assigné", "Score Qualité", 
        "Date Création", "Dernière Modification", "Dernière Activité"
    ]
    
    print("=== POSITION BY POSITION ANALYSIS ===")
    for i, (header, data) in enumerate(zip(expected_headers, row_data)):
        position = i + 1
        print(f"Position {position:2d}: {header:20s} = '{data}'")
        
        # Highlight critical fields
        if header == "Agent Assigné":
            print(f"    ^^^ CRITICAL: Agent Assigné should be 'Patrick Almeida', got: '{data}'")
        elif header == "Score Qualité":
            print(f"    ^^^ CRITICAL: Score Qualité should be '85', got: '{data}'")
    
    print()
    print("=== SEARCH FOR PATRICK ALMEIDA ===")
    for i, data in enumerate(row_data):
        if 'Patrick' in str(data):
            print(f"Found 'Patrick Almeida' at index {i} (position {i+1})")
            print(f"Expected header at this position: {expected_headers[i] if i < len(expected_headers) else 'BEYOND HEADERS'}")
    
    print()
    print("=== SEARCH FOR SCORE 85 ===")  
    for i, data in enumerate(row_data):
        if str(data) == '85':
            print(f"Found score '85' at index {i} (position {i+1})")
            print(f"Expected header at this position: {expected_headers[i] if i < len(expected_headers) else 'BEYOND HEADERS'}")

if __name__ == "__main__":
    debug_row_data_construction()