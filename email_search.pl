#!/usr/bin/perl
###############################################################
# rdryan186@gmail.com
# 2013.10.10
#**************************************************************
# Copyright (c) 2013
###############################################################
use strict;
use warnings;
use LWP::UserAgent;
use Encode;
use URI::Escape;
use Win32::Console;

my $con = Win32::Console->new();
$con->Title("email_search");

my $MAXNUM = 100;	#maximum number in one page
open (FID, ">email_result.csv") or die "Cannot open email_result.csv for write:$!";

$SIG{'INT'} = 'clean_up';
my $delay = 45;

###########################################################################
# Main Porcess
###########################################################################
open (FIN, "<keyword.csv") or die "Cannot open keyword.csv for read:$!";

while (my $word=<FIN>)
{
	chomp($word);
	print "Using keyword $word for searching...\n";
	&main_search($word);
}

close(FIN);
close(FID);
print "The results have been saved to result.xls\n";

###########################################################################
# Sub Routines
###########################################################################
sub main_search{
	my $word = shift;
	
	my $site_web = 'weibo.com';
	my $keyword = "$word site:$site_web";
		
	my $content = &google_search($keyword,0);
	my @emails = &get_emails($content,$word);
	
	my $total = &get_total_results($content);
	my $cycle = int($total/$MAXNUM);
	$cycle += 1 if ( ($total % $MAXNUM) != 0);
	#print "Total results $total\n";
	#printf("It will take %d cycles to get all of the emails.\n",$cycle);
	
	&save_emails(\@emails);	#save this time results
	sleep($delay);
	
	my $i=1;
	while( $i<$cycle && $i<11)	#restrict to 10 cycles
	{
		#printf("this is %d, remain %d cycles\n",$i,$cycle-$i);
		$content = &google_search($keyword,$i*$MAXNUM);
		@emails = &get_emails($content,$word);
		&save_emails(\@emails);
		
		#sleep for 25 seconds to avoid shielding from google
		sleep($delay);
		$i++;
	}

}

sub google_search{
	my $keyword = $_[0];
	my $start = $_[1];
	#print "keyword is $keyword\n";

	#we must first convert our search term into utf8, 
	#then can we use uri_escape to encode the term to search-engine like encoding
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

	my $content = encode("utf8", $response->decoded_content()); #convert to utf8
	#print $content;
	return $content; 
}

sub get_emails{
	my $content = $_[0];
	my $word = $_[1];
	
	$content =~ s/>Cached</></g;
	$content =~ s/<.*?>//g;
	my @emails = $content =~ m/([0-9a-zA-Z][0-9a-zA-Z\._]+\@$word)/g;
	
	return @emails;
}

sub get_total_results{
	my $content=$_[0];
	my $total=0;
	$total=$1 if ($content =~ m/<div id=\"resultStats\">(.*?)results/);
	
	$total =~ s/\D//g;
	#print "Find $total results\n";
	return $total;
}

sub save_emails{
	#save each result to excel file
	my $emails = shift;
	foreach my $email (@$emails)
	{
		print "$email\n";
		print FID "$email\n";
	}
}

sub clean_up{
	close(FIN);
	close(FID);
	die "interrupted, exiting...\n";
}

