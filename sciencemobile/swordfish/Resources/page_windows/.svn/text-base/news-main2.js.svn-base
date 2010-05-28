var win = Titanium.UI.currentWindow;
win.setBarColor('#d70000');
win.showNavBar();

// create table view data object
var data = [];

var xhr = Ti.Network.createHTTPClient();
xhr.open("GET","http://news.sciencemag.org/rss/atom.xml");
xhr.onload = function()
{
	try
	{
		var doc = this.responseXML.documentElement;
		var items = doc.getElementsByTagName("entry");
		var x = 0;
		//var doctitle = doc.evaluate("//channel/title/text()").item(0).nodeValue;
		for (var c=0;c<items.length;c++)
		{
			var item = items.item(c);
			var thumbnails = item.getElementsByTagName("media:thumbnail");
			if (thumbnails && thumbnails.length > 0)
			{
				var media = thumbnails.item(0).getAttribute("url");
				var title = item.getElementsByTagName("title").item(0).text;
                var published = item.getElementsByTagName("published").item(0).text;
                var summary = item.getElementsByTagName("summary").item(0).text;
                    //newdescription = description.split("<"); //remove the link from the description                
				
				var row = Titanium.UI.createTableViewRow({
                    height:'auto'
                });
                
                var summarylabeltop=35;
                
                if(title.length>36){
                	summarylabeltop=50;
                	}

                var publishedlabel = Titanium.UI.createLabel({
                    text:published,
                    color:'#5c5c5e',
                    textAlign:'left',
                    top:2,
                    left:75,
                    width: 'auto',
                    height:'auto',
                    font:{fontWeight:'bold',fontSize:10}
                });
                row.add(publishedlabel);

                var titlelabel = Titanium.UI.createLabel({
                    text:title,
                   
                    textAlign:'left',
                    top:15,
                    left:75,
                    width: 'auto',
                    height:'auto',
                    font:{fontWeight:'bold',fontSize:14}
                });
                row.add(titlelabel);
                
                var summarylabel = Titanium.UI.createLabel({
                    
                    text:summary,
                    //text:title.length,
                    textAlign:'left',
                    color:'#646464',
                    font:{fontSize:13},
                    top:summarylabeltop,
                    //bottom:5,
                    width:'auto',
                    height:'auto',
                    left:75,
                    
                    
                });
                row.add(summarylabel);

                
				var img = Ti.UI.createImageView({
					url:media,
                    top:5,
					left:5,
					bottom:5,
					height:60,
					width:60
				});
				row.add(img);
				data[x++] = row;
				//row.url = item.getElementsByTagName("link").item(0).text;
				row.url = item.getElementsByTagName("link").item(0).getAttribute("href");
				row.passarticle = item.getElementsByTagName("content").item(0).text;
				
			}
		}
		var tableview = Titanium.UI.createTableView({data:data});
		Titanium.UI.currentWindow.add(tableview);
		tableview.addEventListener('click',function(e)
		{
			
			var articleWindow = Titanium.UI.createWindow({			
				backgroundColor:'#ffffff'		
			})
			
			var animateArticle = Titanium.UI.createAnimation();
			animateArticle.height = 460;
			animateDescription.width = 320;
			animateDescription.duration = 300;
			
			var articleBody = Titanium.UI.createLabel({
				text:e.row.passarticle,
				top:50,
				left:5,
				right:5,
				font:{fontSize:14},
				height:250,
				width:300
			
			})
			
			articleWindow.add(articleBody);
			articleWindow.open({transition:Titanium.UI.iPhone.AnimationStyle.CURL_UP});
			
			
			/*
				var w = Ti.UI.createWindow({title:"testing"});
				var wb = Ti.UI.createWebView({url:e.row.url});
				w.add(wb);
	//--------
				var b = Titanium.UI.createButton({
					title:'Close',
					style:Titanium.UI.iPhone.SystemButtonStyle.PLAIN
				});
				w.setLeftNavButton(b);
				b.addEventListener('click',function()
				{
					w.close();
				});
				w.open({modal:true}); 
			*/
			
		});
	}
	catch(E)
	{
		alert(E);
	}
};
xhr.send();


