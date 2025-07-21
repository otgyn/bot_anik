import json
import requests
import os

def load_json_as_dic(path):
    with open(path, 'rb') as f:
        dic = json.load(f)
    return dic
    
def save_dic_as_json(dic,path):
    with open(path, 'w') as f:
        json.dump(dic, f)


def add_song_to_bplist(file_path, info, requester_name = None):
    
    # Load the existing playlist data
    playlist = load_json_as_dic(file_path)

    new_song = build_song_dic(info)
    if requester_name:
        new_song['requester'] = requester_name
    # Append the new song to the songs list
    if 'songs' in playlist and isinstance(playlist['songs'], list):
        playlist['songs'].append(new_song)
    else:
        playlist['songs'] = [new_song]

    # Save the updated playlist data back to file
    save_dic_as_json(playlist,file_path)

def get_songs_from_bplist(file_path):
    # Load the existing playlist data
    playlist = load_json_as_dic(file_path)
    return playlist['songs']

def write_obs_txt(path, text):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(text)


def clear_songs_from_bplist(file_path):
    # Load the existing playlist data
    playlist = load_json_as_dic(file_path)

    # Empty the songs list if it exists
    if 'songs' in playlist and isinstance(playlist['songs'], list):
        playlist['songs'].clear()

    # Save the updated playlist data back to file
    save_dic_as_json(playlist,file_path)

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
        info = load_json_as_dic(file_path)
    else:
        info = get_api_song_info(song_id)
        if info is not None:
            save_dic_as_json(info,file_path)
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
    log = "This track conditions"

    for k,value in conditions.items():
        match k:
            case 'declaredAi':
                if song_info.get(k,'') not in value:
                    return False,' AI generated tracks cannot be addded'
            case 'nsfw':
                if song_info.get(k,False) not in value:
                    return False,' nsfw tracks cannot be addded'
            case 'forbidden_words':
                for word in value:
                    for txt in [song_info.get('name',''),song_info.get('description','')]:                       
                        if txt.lower().find(word) !=-1:
                            return False,'This song seems to contain forbidden words'
            case 'stats':
                for k2,v2 in value.items():
                    match k2:
                        case 'upvotes':
                            if song_info.get('stats',{}).get('upvotes') < v2:
                                return False,f' Track need at least {v2} up votes to be added '
                        case 'score':
                            if song_info.get('stats',{}).get('score') < v2:
                                return False,f' Tracks rating need to be at least {v2}'
            case 'metadata':
                for k2,v2 in value.items():
                    match k2:
                        case 'duration':
                            if (song_info.get('metadata',{}).get('duration') < v2[0]
                            or song_info.get('metadata',{}).get('duration') > v2[1]):
                                return False,f' Track duration need to be beetween {v2[0]} and {v2[1]} seconds'
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
                                    return False,f'At least one of those difficultys need to be available for the track to be allowed: {v2}'            
    return valid,log



if __name__ == "__main__":
    # Example usage
    song_id = "d1cc"
    song_info = get_song_info_by_id(song_id)
    print(song_info)

