import jinja2, os, sys
from TTServer import  currentMessage
from lxml import etree
from utilities import *
import re

Ticketing="""<AMA_RailTicketingInPnrRQ xmlns="http://xml.amadeus.com/RAI/2009/10" Version="5.4">
	<TicketingActions>
		<TicketingAction All="true">
		</TicketingAction>
	</TicketingActions>
	<TransactionOptions KeepRecordInContext="true"/>
</AMA_RailTicketingInPnrRQ>"""


def TicketingRequest(context):
    loader = jinja2.FileSystemLoader(os.getcwd())
    jenv = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
    t2 = jenv.from_string(Ticketing)
    return ''.join(map(unicode.strip,t2.render(myContext=context).splitlines()))

def SyncResponse(context,response):
    print('Ticket json data for GetContentAndRulesV5.py')
    xmlResponse = etree.fromstring(response)
    if xmlResponse.tag.find("AMA_RailGetContentAndRulesInPnrRS") == -1:
        return currentMessage.TTS_MATCH_COMPARISON_FAILURE
    for error in xmlResponse.iter('{*}Error'):
        print "Error in GetContentAndRules: %s : %s" %(error.get('Code'), error.text)
        return currentMessage.TTS_MATCH_COMPARISON_FAILURE
    updatedTickets = []
    for xmlTicket in xmlResponse.iter('{*}Ticket'):
        if xmlTicket.get('Number'):
            ticket = {}
            ticket['number'] = xmlTicket.get('Number')
            ticket['tattoo'] = xmlTicket.get('Tattoo')
            ticket['segmentTattoos'] = []
            ticket['passengerTattoos'] = []
            for xmlTrip in xmlTicket.iter('{*}BookedTrip'):
                ticket['segmentTattoos'].append(xmlTrip.get('Tattoo'))
            for xmlPassenger in xmlTicket.iter('{*}Passenger'):
                ticket['passengerTattoos'].append(xmlPassenger.get('Tattoo'))
            updatedTickets.append(ticket)
    print(updatedTickets)
    print(ticket)
    for schedule in context["journey"]:
        if "tickets" in schedule.keys():
            for ticket in schedule["tickets"]:
                for updatedTicket in updatedTickets:
                    if ticket['number'] == updatedTicket['number']:
                        ticket['tattoo'] = updatedTicket['tattoo']
                        ticket['segmentTattoos'] = updatedTicket['segmentTattoos']
                        ticket['passengerTattoos'] = updatedTicket['passengerTattoos']
    return currentMessage.TTS_MATCH_COMPARISON_OK

def SyncResponseV6(context,response):
    print('Ticket json data for GetContentAndRulesV5.py')
    def getSegmentTattoo(xml,segmentReference,segments):
        for xmlSegment in xml.iter('{*}Segment'):
            print "segment ID %s"%(xmlSegment.get('ID'))
            if xmlSegment.get('ID') == segmentReference:
                xmlStart = xmlSegment.find('{*}start')
                xmlIdentifier = xmlSegment.find('{*}identifier')
                for segment in segments:
                    if ('trainNumber' in segment.keys()) and ('departureDateTime' in segment.keys()):
                        if (segment['trainNumber'] == xmlIdentifier.text) and (segment['departureDateTime'] == xmlStart.get('dateTime')):
                            return segment['tattoo']
    def getPassengerTattoo(xml, passengerReference, passengers):
        for xmlPassenger in xml.iter('{*}Actor'):
            if xmlPassenger.get('ID') == passengerReference:
                xmlName = xmlPassenger.find('{*}Name')
                for passenger in passengers:
                    if (passenger['firstName'] == xmlName.get('FirstName')) and (passenger['lastName'] == xmlName.get('LastName')):
                        return passenger['tattoo']
    xmlResponse = etree.fromstring(response)
    if xmlResponse.tag.find("AMA_RailGetContentAndRulesRS") == -1:
        return currentMessage.TTS_MATCH_COMPARISON_FAILURE
    for error in xmlResponse.iter('{*}Error'):
        print "Error in GetContentAndRules: %s : %s" %(error.get('Code'), error.text)
        return currentMessage.TTS_MATCH_COMPARISON_FAILURE
    updatedTickets = []
    passengers = context['passengers']
    segments = []
    for schedule in context['journey']:
        for segment in schedule['segments']:
            segments.append(segment)
    for xmlTicket in xmlResponse.iter('{*}Contract'):
        if xmlTicket.get('Number'):
            ticket = {}
            ticket['number'] = xmlTicket.get('Number')
            ticket['tattoo'] = xmlTicket.get('LegacyID')
            ticket['segmentTattoos'] = []
            ticket['passengerTattoos'] = []
            ticketReferences = xmlTicket.get('RefIDs')
            for segmentReference in re.findall(r"SEG_[0-9]*",ticketReferences):
                ticket['segmentTattoos'].append(getSegmentTattoo(xmlResponse,segmentReference, segments))
            for passengerReference in re.findall(r"PAX_[0-9]*",ticketReferences):
                ticket['passengerTattoos'].append(getPassengerTattoo(xmlResponse,passengerReference,passengers))
            updatedTickets.append(ticket)
    for schedule in context["journey"]:
        if "tickets" in schedule.keys():
            for ticket in schedule["tickets"]:
                for updatedTicket in updatedTickets:
                    if ticket['number'] == updatedTicket['number']:
                        ticket['tattoo'] = updatedTicket['tattoo']
                        ticket['segmentTattoos'] = updatedTicket['segmentTattoos']
                        ticket['passengerTattoos'] = updatedTicket['passengerTattoos']
    print(updatedTickets)
    print(ticket)
    print prettyPrint(context['step'])
    return currentMessage.TTS_MATCH_COMPARISON_OK