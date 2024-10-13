# Import Necessary Dependencies
import streamlit as st
from twelvelabs import TwelveLabs
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Get the API Key from the Dashboard - https://playground.twelvelabs.io/dashboard/api-key
API_KEY = "tlk_241Z16H2R70KP22J4CV3K22801XG" #os.getenv("API_KEY")

# Create the INDEX ID as specified in the README.md and get the INDEX_ID
INDEX_ID = os.getenv("INDEX_ID")

print(API_KEY)
print(" API_KEY ")
print(INDEX_ID)
print(" INDEX_ID ")

client = TwelveLabs(api_key=API_KEY)

# Background Setting of the Application
page_element = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://wallpapercave.com/wp/wp3589963.jpg");
    background-size: cover;
}
[data-testid="stHeader"] { 
    background-color: rgba(0,0,0,0);
}
[data-testid="stToolbar"] {
    right: 2rem;
    background-image: url("");
    background-size: cover;
}
</style>
"""
st.markdown(page_element, unsafe_allow_html=True)

print("http://localhost:8501/")

# Classes to classify the video into, there are categories name and 
# the prompts which specifc finds that factor to label that category

@st.cache_data
def get_initial_classes():
    return [
        {"name": "AquaticSports", "prompts": ["swimming competition", "diving event", "water polo match", "synchronized swimming", "open water swimming"]},
        {"name": "AthleticEvents", "prompts": ["track and field", "marathon running", "long jump competition", "javelin throw", "high jump event"]},
        {"name": "GymnasticsEvents", "prompts": ["artistic gymnastics", "rhythmic gymnastics", "trampoline gymnastics", "balance beam routine", "floor exercise performance"]},
        {"name": "CombatSports", "prompts": ["boxing match", "judo competition", "wrestling bout", "taekwondo fight", "fencing duel"]},
        {"name": "TeamSports", "prompts": ["basketball game", "volleyball match", "football (soccer) match", "handball game", "field hockey competition"]},
        {"name": "CyclingSports", "prompts": ["road cycling race", "track cycling event", "mountain bike competition", "BMX racing", "cycling time trial"]},
        {"name": "RacquetSports", "prompts": ["tennis match", "badminton game", "table tennis competition", "squash game", "tennis doubles match"]},
        {"name": "RowingAndSailing", "prompts": ["rowing competition", "sailing race", "canoe sprint", "kayak event", "windsurfing competition"]}
    ]

# Session State for the custom classes 
def get_custom_classes():
    if 'custom_classes' not in st.session_state:
        st.session_state.custom_classes = []
    return st.session_state.custom_classes

# Utitlity Function to add the custom classes in app
def add_custom_class(name, prompts):
    custom_classes = get_custom_classes()
    custom_classes.append({"name": name, "prompts": prompts})
    st.session_state.custom_classes = custom_classes
    st.session_state.new_class_added = True

# Utitlity Function to classify all the videos in the specified Index
def classify_videos(selected_classes):
    return client.classify.index(
        index_id=INDEX_ID,
        options=["visual"],
        classes=selected_classes,
        include_clips=True
    )

# To get the video urls from the resultant video id
def get_video_urls(video_ids):
    base_url = f"https://api.twelvelabs.io/v1.2/indexes/{INDEX_ID}/videos/{{}}"
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    video_urls = {}

    for video_id in video_ids:
        try:
            response = requests.get(base_url.format(video_id), headers=headers)
            response.raise_for_status()
            data = response.json()
            if 'hls' in data and 'video_url' in data['hls']:
                video_urls[video_id] = data['hls']['video_url']
            else:
                st.warning(f"No video URL found for video ID: {video_id}")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to get data for video ID: {video_id}. Error: {str(e)}")

    return video_urls

# Utitlity Function to Render the Video by the resultant video url
def render_video(video_url):
    hls_player = f"""
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <div style="width: 100%; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <video id="video" controls style="width: 100%; height: auto;"></video>
    </div>
    <script>
      var video = document.getElementById('video');
      var videoSrc = "{video_url}";
      if (Hls.isSupported()) {{
        var hls = new Hls();
        hls.loadSource(videoSrc);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED, function() {{
          video.pause();
        }});
      }}
      else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
        video.src = videoSrc;
        video.addEventListener('loadedmetadata', function() {{
          video.pause();
        }});
      }}
    </script>
    """
    st.components.v1.html(hls_player, height=300)