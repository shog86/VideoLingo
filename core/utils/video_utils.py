import subprocess
import json

def get_video_info(video_path):
    """Get video information using ffprobe"""
    cmd = [
        'ffprobe', '-v', 'error', 
        '-select_streams', 'v:0', 
        '-show_entries', 'stream=bit_rate,pix_fmt,r_frame_rate', 
        '-of', 'json', video_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        stream = info['streams'][0]
        
        # bit_rate might be missing in some containers, try format
        if 'bit_rate' not in stream:
            cmd_fmt = [
                'ffprobe', '-v', 'error', 
                '-show_entries', 'format=bit_rate', 
                '-of', 'json', video_path
            ]
            result_fmt = subprocess.run(cmd_fmt, capture_output=True, text=True, check=True)
            info_fmt = json.loads(result_fmt.stdout)
            bitrate = info_fmt.get('format', {}).get('bit_rate')
        else:
            bitrate = stream['bit_rate']
            
        return {
            'bitrate': bitrate,
            'pix_fmt': stream.get('pix_fmt'),
            'fps': stream.get('r_frame_rate')
        }
    except Exception as e:
        print(f"Error probing video info: {e}")
        return {}
