#!/usr/bin/perl
###############################################################
# rdryan186@gmail.com
# 2013.09.23
#**************************************************************
# Copyright (c) 2013
###############################################################
use LWP::UserAgent;
use Encode;
use URI::Escape;
use Spreadsheet::WriteExcel;
use Win32::Console;

my $con = Win32::Console->new(standard_handle);
$con->Title("google_search");

my $MAXNUM = 100;	#maximum number in one page
my $workbook = Spreadsheet::WriteExcel->new('result.xls') or die "cannot open result.xls for write:$!";
my $worksheet = $workbook->add_worksheet();

###########################################################################
# Get Keywords, from User input
###########################################################################
my $keyword;
my $word;
my $site_web;

print "Please input your site website:\n";
$site_web = <STDIN>;
print "Please input your keyword for searching:\n";
$word = <STDIN>;

$keyword = "$word site:$site_web";
#$keyword = "skype site:www.cpan.org";
#$keyword = "skype site:www.microsoft.com";

###########################################################################
# Main Porcess
###########################################################################
my $row=0;
my $content = &google_search($keyword,0);
&save_urls($content);	#save this time results

my $total = &get_total_results($content);
my $cycle = int($total/$MAXNUM);
$cycle += 1 if ( ($total % $MAXNUM) != 0);
print "Total results $total\n";
printf("It will take %d cycles to get all of the urls.\n",$cycle);

my $i=1;
while( $i<$cycle)
{
	printf("this is %d, remain %d cycles\n",$i,$cycle-$i);
	$content = &google_search($keyword,$i*$MAXNUM);
	&save_urls($content);
	
	if ( $i % 10 == 9)
	{
		print "Continue or Not?[Y|N]";
		my $choice=<STDIN>;
		chomp($choice);
		if ($choice eq 'N')
		{
			print "You select to quit the search\n";
			last;
		}
	}

	#sleep for 5 seconds to avoid shielding from google
	sleep(5);
	$i++;
}

print "The results have been saved to result.xls\n";

####################################################################
sub google_search{
	my $keyword = $_[0];
	my $start = $_[1];
	#print "keyword is $keyword\n";

	#we must first convert our search term into utf8, 
	#then can we use uri_escape to encode the term to search-engine like encoding
	#my $search = encode("utf-8",decode("gb2312", $keyword)); 
	my $search = encode("utf-8",$keyword); 
	$search = uri_escape($search);

	#print "keyword is $search\n";

	my $ua = new LWP::UserAgent; #Construct the request object

	#add random in agent to avoid google shielding
	if (int(rand(2)) == 1) {
		$ua->agent( "Mozilla/5.0 (X11; Linux i686; rv:2.0.0) Gecko/20100101" ); #Google checks UAs
	} else {
		$ua->agent( "Mozilla/5.0 (X11; Linux i686; rv:2.0.0) Chrome/28.0.1500.95 Safari/537.36" );
	}

	
	$ua->timeout( 10 ); #Give up after 10 seconds of waiting
	$ua->max_redirect( 2 ); #We only want the URL that google sends, so stop after we submit
	$ua->env_proxy; #Load proxy info from the environment, if any is set

	my $response = $ua->get(
		"http://www.google.com/search?&hl=en&num=$MAXNUM&q=".$search."&start=$start" #The URL to request
	) or die( $! );

	#my $firstUrl = $response->contents; #This contains the link of the result page
	my $content = encode("utf8", $response->decoded_content()); #convert to utf8
	#print $content;
	return $content; 
}

sub get_urls{
	my $content=$_[0];
	
	$_ = $content;
	#my @urls = m/a href=\"\/url\?q=(.*?)\" target/g;
	my @urls = m/a href=\"\/url\?q=(.*?)\"/g;
	
	#delete urls that contains http://webache
	my @ret;
	foreach my $line (@urls) {
		$line =~ s/\&amp.*//;
		push @ret,$line if ($line !~ /http:\/\/webcache/)
	}
	
	return @ret;
}

sub get_total_results{
	my $content=$_[0];
	my $total=0;
	$total=$1 if ($content =~ m/<div id=\"resultStats\">(.*?)results/);
	
	$total =~ s/\D//g;
	#print "Find $total results\n";
	return $total;
}

sub save_urls{
	#save each result to excel file
	my $content = $_[0];
	my @urls = &get_urls($content);
	foreach my $url (@urls)
	{
		#print "$url\n";
		$worksheet->write($row,0,$url);
		$row++;
	}
}
