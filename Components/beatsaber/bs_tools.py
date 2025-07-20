import json
import requests
import os

def add_song_to_bplist(file_path, info):
    
    # Load the existing playlist data
    with open(file_path, 'rb') as f:
        playlist = json.load(f)
    new_song = build_song_dic(info)
    # Append the new song to the songs list
    if 'songs' in playlist and isinstance(playlist['songs'], list):
        playlist['songs'].append(new_song)
    else:
        playlist['songs'] = [new_song]

    # Save the updated playlist data back to file
    with open(file_path, 'w') as f:
        json.dump(playlist, f)

def get_songs_from_bplist(file_path):
    # Load the existing playlist data
    with open(file_path, 'rb') as f:
        playlist = json.load(f)
    return playlist['songs']

def write_obs_txt(path, text):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(text)


def clear_songs_from_bplist(file_path):
    # Load the existing playlist data
    with open(file_path, 'rb') as f:
        playlist = json.load(f)

    # Empty the songs list if it exists
    if 'songs' in playlist and isinstance(playlist['songs'], list):
        playlist['songs'].clear()

    # Save the updated playlist data back to file
    with open(file_path, 'w') as f:
        json.dump(playlist, f)

def get_api_song_info(song_id):
    url = f"https://api.beatsaver.com/maps/id/{song_id}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Unable to fetch data for song ID {song_id}")
        return None


def get_song_info_by_id(song_id):
    song_file = f"{song_id}.json"
    cache_dir = "./cached_songs"

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    file_path = os.path.join(cache_dir, song_file)

    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            info = json.load(f)
    else:
        info = get_api_song_info(song_id)
        if info is not None:
            with open(file_path, 'w') as f:
                json.dump(info, f)
    return info

def build_song_dic(song_info):
    last_version = song_info.get('versions',[{}])[-1]
    song_dict = {
        'key':song_info.get('id'),
        'hash':last_version.get('hash'),
        'songName': song_info.get('name','unk')
    }
    return song_dict


    
to_watch ={
    'declaredAi' : ['None'],
    'stats': {
        'upvotes': 50,
        'score': .75,
    },
    'metadata': {
        'duration' : (75, 300),
    },
    'versions': {

            'diffs': ['Easy', 'Normal', 'Hard'],                
        
        }

    }
    
def check_song_conditions(song_info,conditions=to_watch):
    valid = True
    log = "Songs Match all conditions"

    for k,value in conditions.items():
        match k:
            case 'declaredAi':
                if song_info.get('declaredAi','') not in value:
                    return False,' AI generated'
            case 'stats':
                for k2,v2 in value.items():
                    match k2:
                        case 'upvotes':
                            if song_info.get('stats',{}).get('upvotes') < v2:
                                return False,f' up votes < {v2}'
                        case 'score':
                            if song_info.get('stats',{}).get('score') < v2:
                                return False,f' rating < {v2}'
            case 'metadata':
                for k2,v2 in value.items():
                    match k2:
                        case 'duration':
                            if (song_info.get('metadata',{}).get('duration') < v2[0]
                            or song_info.get('metadata',{}).get('duration') > v2[1]):
                                return False,f' duration not in range{v2} seconds'
            case 'versions':
                last = song_info.get('versions',[None])[-1]
                if last is not [None]:
                    for k2,v2 in value.items():
                        match k2:
                            case 'diffs':
                                diff_list = last.get('diffs',[])
                                difficulty_check = False
                                for diff in diff_list:
                                    if diff.get('difficulty',None) in v2:
                                        difficulty_check = True
                                        break
                                if not difficulty_check:
                                    return False,f'no difficulty in {v2} for this track'            
    return valid,log



if __name__ == "__main__":
    # Example usage
    song_id = "48802"
    song_info = get_song_info_by_id(song_id)
    print(song_info)

