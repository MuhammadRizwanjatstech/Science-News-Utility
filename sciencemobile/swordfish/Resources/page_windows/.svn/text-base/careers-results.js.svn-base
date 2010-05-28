var win = Titanium.UI.currentWindow;
win.setBarColor('#d70000');

// create table view data object
var data = [];


//alert
var alertBox = Titanium.UI.createAlertDialog({
	title:'No search results',
	message:'There were no search results. Please go back and try a different keyword'
});



var searchTerm = "http://scjobs.sciencemag.org/JobSeekerX/SearchJobsRSS.asp?kwrd=" + win.search;
var xhr = Ti.Network.createHTTPClient();
xhr.open("GET", searchTerm);
xhr.onload = function()
{
	try
	{
		var doc = this.responseXML.documentElement;
		var items = doc.getElementsByTagName("item");
		var x = 0;
		var doctitle = doc.evaluate("//channel/title/text()").item(0).nodeValue;
		if(!items){
			alertBox.show();
			}
		else {	
			for (var c=0;c<items.length;c++)
			{
				var item = items.item(c);		
				var title = item.getElementsByTagName("title").item(0).text;
				
	   	        var description = item.getElementsByTagName("description").item(0).text;      
				
				
				
				
				
				
				
				var clean = description.replace(/<[^<>]*>/gi, "");
				
				
				var row = Ti.UI.createTableViewRow({
                    height:70,
                    //separatorColor:'#390A0E',
                    //backgroundColor:'#390A0E'
                });
                //row.rightImage = 'images/indicator.png';
                //row.leftImage = 'images/indicator.png';
				//description = description.replace("<p>", "");
				//descrption = description.replace("<b>", "");
				//description = description.replace("<i>", "");
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
				
				
				
				row.desc = clean;
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
			var descriptionWindow = Titanium.UI.createWindow({
					
					backgroundColor:'#ffffff',
					
			});
			var animateDescription = Titanium.UI.createAnimation();
			animateDescription.height = 460;
			animateDescription.width = 320;
			animateDescription.duration = 300;

			// create a button to close window
			var itemTitle = Titanium.UI.createLabel({
				
				text:e.row.passtitle,
				top:10,
				textAlign:'center',
				left:5,
				right:5,
      	        font:{fontSize:16},
				height:'auto',
				width:300
				
			});			
			var itemDescription = Titanium.UI.createLabel({
				//text:title,
				text:e.row.desc,
				top:50,
				left:5,
				right:5,
      	        font:{fontSize:14},
				height:250,
				width:300,
				
			});
			
			var closeButton = Titanium.UI.createButton({
				title:'Close',
				height:30,
				width:150,
				bottom:30
			});
			
			var emailButton = Titanium.UI.createButton({
				title:'E-mail job',
				height:30,
				width:150,
				bottom:70
			});
			
			
			descriptionWindow.add(closeButton);
			descriptionWindow.add(itemTitle);
			descriptionWindow.add(itemDescription);
			descriptionWindow.add(emailButton);
			descriptionWindow.open({transition:Titanium.UI.iPhone.AnimationStyle.CURL_UP});
			
			

			closeButton.addEventListener('click', function()
			{
				
				descriptionWindow.close({transition:Titanium.UI.iPhone.AnimationStyle.CURL_DOWN});
			});
			
			emailButton.addEventListener('click', function()
			{
				var emailDialog = Titanium.UI.createEmailDialog()
				emailDialog.setSubject('Science Careers Job Search Result');
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


