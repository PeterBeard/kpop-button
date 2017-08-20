function load_kpop(callback) {
    let DATA_URL = "top-all-time.json";

    var request = new XMLHttpRequest();
    request.overrideMimeType("application/json");
    request.open("GET", DATA_URL, true);
    request.onreadystatechange = function() {
        if(request.readyState == 4 && request.status == "200") {
            callback(request.responseText);
        }
    };
    request.send();
}

var videos;
var player;
var click_cooldown = false;
function onYouTubeIframeAPIReady() {
  player = new YT.Player('player', {
    height: '540',
    width: '960',
    videoId: videos[0].id,
    events: {
      'onReady': onPlayerReady,
      'onStateChange': onPlayerStateChange
    }
  });
}

function onPlayerReady(event) {
  event.target.playVideo();
}

function onPlayerStateChange(event) {
    // 0 is ended, -1 is error. Either way, play the next video.
    if(player.getPlayerState() <= 0) {
        document.getElementById("kpop-button").click();
    }
}

function random_bg(bgs) {
    let choice = randint(0, bgs.length);
    let body = document.getElementsByTagName("body")[0];
    body.className = "gif";
    body.style.backgroundImage = "url('i/bg/" + bgs[choice] + ".gif')";
}

function init() {
    // Randomize the background image
    let bgs = new Array(
        "chu",
        "dance-2",
        "glasses",
        "omg",
        "party-time",
        "psy",
        "roulette",
        "suran",
        "tv",
        "wow",
        "ya",
        "yesiam",
        "yuha"
    );
    random_bg(bgs);

    // Set up the YouTube API
    var tag = document.createElement('script');

    tag.src = "https://www.youtube.com/iframe_api";
    var firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

    // Load the list of K-Pop videos
    load_kpop(function(json) {
        videos = shuffle_array(JSON.parse(json));
        document.getElementById("current-index").value = 1;
        // Play a random video
        document.getElementById("kpop-button").addEventListener("click", function() {
            let curr_element = document.getElementById("current-index");
            let curr_video = curr_element.value * 1;
            if(curr_video >= videos.length) {
                curr_video = 0;
                videos = shuffle_array(videos);
            }
            play_video(videos[curr_video]);
            curr_element.value = curr_video + 1;
        });
    });
}

function play_video(video) {
    if(!click_cooldown) {
        player.loadVideoById(video.id, 0, "large");
    }
    click_cooldown = true;
    setTimeout(function() { click_cooldown = false; }, 500);
}

function randint(min, max) {
    return Math.floor(Math.random() * (max - min) + min);
}

function shuffle_array(arr) {
    for(let i = 0; i < arr.length; i++) {
        let j = randint(i, arr.length);
        let v = arr[i];
        arr[i] = arr[j];
        arr[j] = v;
    }
    return arr;
}

window.addEventListener("load", init);
