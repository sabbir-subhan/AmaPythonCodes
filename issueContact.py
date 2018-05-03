import jinja2, os, sys
from TTServer import  currentMessage
from lxml import etree
from utilities import *
import re

Ticketing="""<AMA_RailIssueContractRQ Version="1.000" xmlns="http://xml.amadeus.com/2010/06/RailTicketing_v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:mop="http://xml.amadeus.com/2010/06/PayIssueTypes_v1" xmlns:rail="http://xml.amadeus.com/2010/06/RailCommonTypes_v2">
<AssociatedRecords TID="RCD_1" Identifier="{{ myContext['recordLocator'] }}"/>
	<Issue>
			<rail:MethodOfPayment TID="MOP_2">
			<mop:Cash/>
		</rail:MethodOfPayment>
	<rail:FormatAndDelivery>
	<rail:Delivery Type="006" DistributionType="004" TID="TKO_3"/>
	</rail:FormatAndDelivery>
	<rail:Contract TID="CTR_1" RefTIDs="RCD_1 MOP_2 TKO_3"/>
	</Issue>
</AMA_RailIssueContractRQ>"""

TicketingPayAndTicket="""<AMA_RailIssueContractRQ Action="PayAndTicket" Version="1.000" xmlns="http://xml.amadeus.com/2010/06/RailTicketing_v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:mop="http://xml.amadeus.com/2010/06/PayIssueTypes_v1" xmlns:rail="http://xml.amadeus.com/2010/06/RailCommonTypes_v2">
<AssociatedRecords TID="RCD_1" Identifier="{{ myContext['recordLocator'] }}"/>
    <AdditionalData>
        <rail:Data TID="AD_3" Name="backUrl_Success">
        https://www.google.com/search?q=success</rail:Data>
        <rail:Data TID="AD_4" Name="backUrl_Retry">
        https://www.google.com/search?q=retry</rail:Data>
        <rail:Data TID="AD_5" Name="backUrl_Failure">
        https://www.google.com/search?q=failure</rail:Data>
        <rail:Data TID="AD_6" Name="sessionTimeout">
        999</rail:Data>
    </AdditionalData>
</AMA_RailIssueContractRQ>"""


def IssueContract(context):
    loader = jinja2.FileSystemLoader(os.getcwd())
    jenv = jinja2.Environment(trim_blocks=True, lstrip_blocks=True)
    if 'payment' in context['step']:
        t2 = jenv.from_string(TicketingPayAndTicket)
    else:
        t2 = jenv.from_string(Ticketing)
    return ''.join(map(unicode.strip,t2.render(myContext=context).splitlines()))

def IssueContractResponse(context,response):
    def getSegmentTattoo(xml,segmentReference,segments):
        for xmlSegment in xml.iter('{*}Segment'):
            if xmlSegment.get('ID') == segmentReference:
                xmlStart = xmlSegment.find('{*}start')
                for segment in segments:
                    if segment['trainNumber'] == xmlSegment.find('{*}identifier').text and segment['departureDateTime'] == xmlStart.get('dateTime'):
                        return segment['tattoo']
    def getPassengerTattoo(xml, passengerReference, passengers):
        for xmlPassenger in xml.iter('{*}Actor'):
            if xmlPassenger.get('ID') == passengerReference:
                xmlName = xmlPassenger.find('{*}Name')
                for passenger in passengers:
                    if passenger['firstName'] == xmlName.get('FirstName') and passenger['lastName'] == xmlName.get('LastName'):
                        return passenger['tattoo']
    def getTickets(xml, segments, passengers):
        tickets = []
        for xmlTicket in xml.iter('{*}Contract'):
            ticket = {}
            ticket['number'] = xmlTicket.get('Number')
            ticket['tattoo'] = xmlTicket.get('LegacyID')
            ticketReferences = xmlTicket.get('RefIDs')
            ticket['segmentTattoos'] = []
            for segmentReference in re.findall(r"SEG_[0-9]*",ticketReferences):
                ticket['segmentTattoos'].append(getSegmentTattoo(xml,segmentReference, segments))
            ticket['passengerTattoos'] = []
            for passengerReference in re.findall(r"PAX_[0-9]*",ticketReferences):
                ticket['passengerTattoos'].append(getPassengerTattoo(xml,passengerReference,passengers))
            for segment in segments:
                if segment['tattoo'] in ticket['segmentTattoos']:
                    tickets.append(ticket.copy())
        print (ticket)
        return tickets
    xmlResponse = etree.fromstring(response)
    if xmlResponse.tag.find("AMA_RailIssueContractRS") == -1:
        return currentMessage.TTS_MATCH_COMPARISON_FAILURE
    for error in xmlResponse.iter('{*}Error'):
        print "Error in RailIssueContract: %s : %s" %(error.get('Code'), error.text)
        return currentMessage.TTS_MATCH_COMPARISON_FAILURE
    if 'payment' in context['step']:
        for xmlData in xmlResponse.iter('{*}Data'):
            if xmlData.get('Name') == 'PAYMENT_URL':
                context['paymentUrl'] = xmlData.text
                break
    else:
        for schedule in context["journey"]:
            #update the context only for the applicable schedules as requested in the step
            if schedule['ID'] in context['step']['schedules']:
                schedule['tickets'] = getTickets(xmlResponse,schedule['segments'], context['passengers'])
    print prettyPrint(context['step'])
    return currentMessage.TTS_MATCH_COMPARISON_OK