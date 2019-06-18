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
    // get data from python. 
    var url = `/scrape/${input}`;
    d3.json(url).then(function(response){
        console.log(response);

        // separate them store into variable
        // each in the form - [{word: "sql", freq:123}]
        var unigram = response[0];
        var bigram = response[1];
        var company = response[2];
        var location = response[3];

        // pass n-grams to barChart for plotting
        barChart(unigram);
        bigramChart(bigram);
        map(company);
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
    $('#loader').fadeOut(50, function(){ $('#loader').remove(); });

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
};

function map(company){
    
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

    console.log('map working up to line 148')

    // var cities =  [{
    //     location: [37.5665, 126.5780],
    //     name: "Oracle",
    //     position: "Data Analytics"
    //     },
    //     {
    //     location: [37.1665, 126.9780],
    //     name: "Bank of America",
    //     position: "Data Analyst"
    //     },
    //     {
    //     location: [37.5665, 126.5780],
    //     name: "Axiologic Solutions",
    //     position: "Data Analyst"
    //     },
    //     {
    //     location: [37.5665, 126.5550],
    //     name: "Bloomberg",
    //     position: "Market Data Analyst"
    //     },
    //     {
    //     location: [37.5165, 126.5780],
    //     name: "Mercedes-benz",
    //     position: "Financial Analst"
    //     },
    //     {
    //     location: [37.5965, 126.5980],
    //     name: "Oracle",
    //     position: "Data Analytics"
    //     },
    //     {
    //     location: [37.7665, 126.7770],
    //     name: "Bank of America",
    //     position: "Data Analyst"
    //     },
    //     {
    //     location: [37.5665, 126.3380],
    //     name: "Axiologic Solutions",
    //     position: "Data Analyst"
    //     },
    //     {
    //     location: [37.3665, 126.5780],
    //     name: "Bloomberg",
    //     position: "Market Data Analyst"
    //     },
    //     {
    //     location: [37.7665, 126.5780],
    //     name: "Mercedes-benz",
    //     position: "Financial Analst"
    //     }
    //     ];
    for (var i = 0; i < cities.length; i++) {
        var city = cities[i];
        L.marker([37.7665, 126.5780])
            .bindPopup("<h1>" + company[i] + "</h1>")
            .addTo(myMap);
        };
};

