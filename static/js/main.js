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
    console.log(title);
    console.log(loc);


    // Since HTTP only allow to send string we split title and location by "/" which
    // we will split in python to separate two words.
    var input = title +"!" + loc
    console.log(input);
   
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

        // pass n-grams to barChart for plotting
        barChart(unigram);
    });
};

function barChart(list_of_dicts){
    // map function to store words in one list and frequency on another
    var words = list_of_dicts.map(x => x.word); // [word1, word2,....]
    var freqs = list_of_dicts.map(x => x.freq); // [freq1, freq2, ...]
    
    console.log(words);
    console.log(freqs);
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
        autosize:true,
        yaxis:{
            title:"top 100 most frequent uni-gram words",
            ticktext:words,
            automargin:true
        }
    };

    Plotly.newPlot('unigram-chart', data, layout);
};