var win = Titanium.UI.currentWindow;
win.setBarColor('#d70000');
win.showNavBar();

// create table view data object
var data = [];

//alert
var alertBox = Titanium.UI.createAlertDialog({
	title:'Connection error',
	message:'Check your internet connection and try again'
});


var xhr = Ti.Network.createHTTPClient();
xhr.open("GET", "http://news.sciencemag.org/rss/atom.xml");
xhr.onload = function()
{
	try
	{
		var doc = this.responseXML.documentElement;
		var items = doc.getElementsByTagName("entry");
		var x = 0;
		//var doctitle = doc.evaluate("//channel/title/text()").item(0).nodeValue;
		if(!items){
			alertBox.show();
			}
		else {	
			for (var c=0;c<items.length;c++)
			{
				var item = items.item(c);		
				var title = item.getElementsByTagName("title").item(0).text;
	   	        var summary = item.getElementsByTagName("summary").item(0).text;      
				var thumbnails = item.getElementsByTagName("media:thumbnail");
				var media = thumbnails.item(0).getAttribute("url");
							
				var row = Ti.UI.createTableViewRow({
                    height:70,
                
                });
           

				var label = Ti.UI.createLabel({
					text:title,
					left:5,
					top:5,
					bottom:5,
					right:5,
      	          font:{fontSize:14}
				});
				
				row.add(label);
			
			
				data[x++] = row;
				
				
				
				
				row.passmedia = media;	
				
				row.passauthor = item.getElementsByTagName("title").item(0).text;
				row.passarticle = item.getElementsByTagName("content").item(0).text;
				row.passtitle = item.getElementsByTagName("title").item(0).text;
                row.url = item.getElementsByTagName("link").item(0).text;
				
			}
		}	
		var tableview = Titanium.UI.createTableView({data:data});
		Titanium.UI.currentWindow.add(tableview);
		tableview.addEventListener('click',function(e)	//what happens when an article gets clicked
		{
		
			if (Ti.Platform.name == 'android') {
				options.navBarHidden = true;
			}
			var articleWindow = Titanium.UI.createWindow({
					
					backgroundColor:'#ffffff',
					title:'Latest News'
					
			});
			var animateArticle = Titanium.UI.createAnimation();
			animateArticle.height = 420;
			animateArticle.width = 320;
			animateArticle.duration = 300;

			var entryTitle = Titanium.UI.createLabel({
				text:e.row.passtitle,
				top:10,
				textAlign:'center',
				left:5,
				right:5,
      	        font:{fontSize:16},
				height:'auto',
				width:300
				
			});			

			var webView = Titanium.UI.createWebView({
				
				top:40,
				
				html:"<html><body><table><tr><td valign=\"top\"><img src=\""+e.row.passmedia+"\" /></td><td><h3>"+e.row.passtitle+"</h3></td></tr><tr><td colspan=\"2\"> <span style=\"color:#666666\">by "+e.passauthor+"</span></td></tr></table>"+e.row.passarticle+"</body></html>"
			})
			
		
			var label = Titanium.UI.createButton({
				title:'Latest News',
				backgroundColor:'#d70000',
				style:Titanium.UI.iPhone.SystemButtonStyle.PLAIN
			});
		
			var flexSpace = Titanium.UI.createButton({
				systemButton:Titanium.UI.iPhone.SystemButton.FLEXIBLE_SPACE
			});
			var closeButton = Titanium.UI.createButton({
				title:'Close',
				style:Titanium.UI.iPhone.SystemButtonStyle.DONE
			});
			var emailButton = Titanium.UI.createButton({
				title:'E-mail this',
				style:Titanium.UI.iPhone.SystemButtonStyle.BORDERED
			});



			var toolbar = Titanium.UI.createToolbar({
				items:[closeButton,flexSpace,label, flexSpace,emailButton],
				top:0,
				borderTop:false,
				borderBottom:true,

			})
			
			articleWindow.add(toolbar);		
			articleWindow.add(webView);
			

			articleWindow.open({transition:Titanium.UI.iPhone.AnimationStyle.CURL_UP});
			

			closeButton.addEventListener('click', function()
			{
				
				articleWindow.close({transition:Titanium.UI.iPhone.AnimationStyle.CURL_DOWN});
			});
			
			emailButton.addEventListener('click', function()
			{
				var emailDialog = Titanium.UI.createEmailDialog()
				emailDialog.setSubject('Science News');
				emailDialog.setMessageBody('I am forwarding you this job listing from Science Careers because I think you may find it useful \n\n'+e.row.url + '\n\n For more job listings, visit http://sciencescareers.sciencemag.org');
				emailDialog.setBarColor('#d70000');
				//emailDialog.open(descriptionWindow,{animated:true});
				emailDialog.open();
			});


	
		});
	}
	catch(E)
	{
		alert(E);
	}
};
xhr.send();


