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

    // console.log(title);
    // console.log(loc);


    // Since HTTP only allow to send string we split title and location by "/" which
    // we will split in python to separate two words.
    var input = title +"!" + loc

    // console.log(input);
   
    // send it off to scrape function 
    scrape(input);
});

function scrape(input){
    // send input to python
    var url = `/scrape/${input}`;
    d3.json(url).then(function(response){
        console.log(response);

        // separate them store into variable
        // each in the form - [{word: "sql", freq:123}]
        var unigram = response[0];
        var bigram = response[1];
        console.log(unigram)
        console.log(bigram)
        

        // pass n-grams to barChart for plotting
        barChart(unigram);
        bigramChart(bigram);
    });
};

function barChart(list_of_dicts){
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
        }
    };

    // Delete data loader before loading any chart
    $('#loader').fadeOut(500, function(){ $('#loader').remove(); });



    Plotly.newPlot('unigram-chart', data, layout);
};

function bigramChart(list_of_dicts){
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
        }
    };

    Plotly.newPlot('bigram-chart', data, layout);

    // Calling map function after all ploting is done.
    map();
};

function map(){
    
    var myMap = L.map('myMap', {
        center:[45.5017, -73.5673],
        zoom:3
    });
    L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiaGFuZXVsa2ltMjE0IiwiYSI6ImNqdnB0cjJtMjJkMmM0NW9pNmN0bjFyZjUifQ.v8Hz5-t66g5-AmrRQXDfDQ", {
        maxZoom: 18,
        id: "mapbox.streets-basic"
    }).addTo(myMap);

    var cities =  [{
        location: [40.7128, -74.0059],
        name: "New York",
        population: "8,550,405"
        },
        {
        location: [41.8781, -87.6298],
        name: "Chicago",
        population: "2,720,546"
        },
        {
        location: [29.7604, -95.3698],
        name: "Houston",
        population: "2,296,224"
        },
        {
        location: [34.0522, -118.2437],
        name: "Los Angeles",
        population: "3,971,883"
        },
        {
        location: [41.2524, -95.9980],
        name: "Omaha",
        population: "446,599"
        }
        ];
    for (var i = 0; i < cities.length; i++) {
        var city = cities[i];
        L.marker(city.location)
            .bindPopup("<h1>" + city.name + "</h1> <hr> <h3>Population " + city.population + "</h3>")
            .addTo(myMap);
        };
};

