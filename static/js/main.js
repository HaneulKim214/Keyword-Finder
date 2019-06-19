// give reference to "Go Search" button
var go_search = d3.select("#submit");

go_search.on("click", function(){
    d3.event.preventDefault();
    
    // grab input value and store into variable
    var title = d3.select("#job-title").node().value;
    var loc = d3.select("#job-loc").node().value;
    
    // refresh search bars
    d3.select("#job-title").node().value = "";
    d3.select("#job-loc").node().value = "";

    // Since HTTP only allow to send string we split title and location by "!" which
    // we will split in python to separate two words.
    var input = title + "!" + loc

    // send it off to scrape function 
    scrape(input);
});

function scrape(input){
    // get data from python route("/scrape/<input>"). 
    var url = `/scrape/${input}`;
    d3.json(url).then(function(response){
        console.log(response);

        // separate them store into variable
        // each in the form - [{word: "sql", freq:123}]
        var unigram = response[0];
        var bigram = response[1];
        var geocode = response[2];
        var company = response[3];

        // pass n-grams to barChart for plotting
        unigramChart(unigram);
        bigramChart(bigram);
        map(geocode, company);
    });
};

function unigramChart(list_of_dicts){
    // map function to store words in one list and frequency on another
    var words = list_of_dicts.map(x => x.word); // [word1, word2,....]
    var freqs = list_of_dicts.map(x => x.freq); // [freq1, freq2, ...]
    
    // console.log(words);
    // console.log(freqs);
    var data = [{
        x: freqs,
        y: words,
        type:"bar",
        orientation:"h",
        marker:{
            color:"rgba(55,128,191,0.6)"
        }
    }];

    var layout = {
        autosize:false,
        width:1500,
        height:1000,
        margin: {
            l: 50,
            r: 50,
            b: 100,
            t: 100,
            pad: 4
          },
        plot_bgcolor: '#c7c7c7',
        yaxis:{
            title:"top 50 most frequent uni-gram words",
            titlefont:{size:30},
            ticktext:words,
            automargin:true
        },
        xaxis:{
            title:"Frequency (count)",
            titlefont:{
                size:30
            }
        }
    }

    // Delete data loader before loading any chart
    $('#loader').fadeOut(50, function(){ $('#loader').remove(); });

    Plotly.newPlot('unigram-chart', data, layout);
};

function bigramChart(list_of_dicts){
    // map function to store words in one list and frequency on another
    var words = list_of_dicts.map(x => x.word); // [word1, word2,....]
    var freqs = list_of_dicts.map(x => x.freq); // [freq1, freq2, ...]
    var data = [{
        x: freqs,
        y: words,
        type:"bar",
        orientation:"h",
        marker:{
            color:"rgba(63,191,99,0.6)"
        }
    }];

    var layout = {
        autosize:false,
        width: 1500,
        height: 1000,
        margin: {
            l: 50,
            r: 50,
            b: 100,
            t: 100,
            pad: 4
          },
          plot_bgcolor: '#c7c7c7',
        yaxis:{
            title:"top 50 most frequent bi-gram words",
            titlefont:{size:30},
    
            ticktext:words,
            automargin:true
        },
        xaxis:{
            title:"Frequency (count)",
            titlefont:{
                size:30
            }
        }
    };

    Plotly.newPlot('bigram-chart', data, layout);
};



// -------------- Heat map of Job location --------------
function map(geocode, company){

    var lat = geocode.map(x => x.lat);
    var lng = geocode.map(x => x.lng);

    // get distinct geocode
    distinct_geocode = distinct_geocode(lat,lng);
    console.log(distinct_geocode);

    var myMap = L.map('myMap', {
        center:[37.5665, 126.9780],
        zoom:10
    });
    L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
        attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
        maxZoom: 18,
        id: "mapbox.streets-basic",
        accessToken: API_KEY
    }).addTo(myMap);

    console.log('map working up to line 159')


    distinct_geocode.forEach(function(geocode){
        // notice geocode = [lat,lng]
        L.marker(geocode)
            .bindPopup()
            .addTo(myMap);
    });

};

function distinct_geocode(lat, lng){

  lat_lng = [];
  for (var i = 0; i < lat.length; i++){
  
    lat_str = lat[i].toString()
    lng_str = lng[i].toString()
  
    lat_lng.push(lat_str + "," + lng_str)
  };
  
  lat_lng = new Set(lat_lng);
  
  distinct_lat_lng = [];
  
  lat_lng.forEach(function(x){
    r = x.split(",");
    // change r =[lat,lng] to int
    for (var i =0; i<r.length; i++) {
      r[i] = +r[i]
    } 
    
    distinct_lat_lng.push(r);
  });
  return distinct_lat_lng;
};
