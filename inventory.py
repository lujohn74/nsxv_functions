import requests,os,xml.dom.minidom,json,re
requests.packages.urllib3.disable_warnings()
import xml.etree.ElementTree as ET
nsxmgr="192.168.0.66"
nsx_username="admin"
nsx_password="Nicira123$"
header={"Content-type":"application/xml","Accept":"text/plain"}

def get_scope():
    url="https://"+nsxmgr+"/api/2.0/vdn/scopes"
    conn=requests.get(url,auth=(nsx_username,nsx_password),verify=False)
    output=conn.text
    root=ET.fromstring(output)
    for child in root.findall('vdnScope'):
	scope=child.find('id').text
	return scope

#scope_id=get_scope()
#print scope_id

def get_domain():
    url="https://"+nsxmgr+"/api/1.0/nsx/cli?action=execute"
    body="<nsxcli><command>show cluster all</command></nsxcli>"
    conn=requests.post(url,auth=(nsx_username,nsx_password),verify=False,headers=header,data=body)
    output=conn.text
    print "*" * 100
    print "vCenter Cluster Information"
    print "*" * 100
    print output
    domain=re.findall("domain-c.{1,4}",output)
    return domain
    
cluster=get_domain()

def get_host():
    for domain in cluster:
	url="https://"+nsxmgr+"/api/1.0/nsx/cli?action=execute"
    	body="<nsxcli><command>show cluster %s</command></nsxcli>" %domain
        conn=requests.post(url,auth=(nsx_username,nsx_password),verify=False,headers=header,data=body)
        output=conn.text
        print "*" * 100
        print "Prepared Host Information"
        print "*" * 100
        print output
        host=re.findall("host-.{1,5}",output)
	return host

host=get_host()

def host_healthy():
    for health in host:
        url="https://"+nsxmgr+"/api/1.0/nsx/cli?action=execute"
        body="<nsxcli><command>show host  %s health-status</command></nsxcli>" %health
        conn=requests.post(url,auth=(nsx_username,nsx_password),verify=False,headers=header,data=body)
        output=conn.text
        print "*" * 100
        print "The %s health status" %health +str("\n") + output

# This function causes longer waiting for health status collectiong, we may use it for health collection purpose.
#host_healthy()

def list_lsw():
    url="https://"+nsxmgr+"/api/1.0/nsx/cli?action=execute"
    body="<nsxcli><command>show logical-switch list all</command></nsxcli>"
    conn=requests.post(url,auth=(nsx_username,nsx_password),verify=False,headers=header,data=body)
    output=conn.text
    print "The Logical Switch List" 
    print output

list_lsw()


def list_dlr():
    url="https://"+nsxmgr+"/api/1.0/nsx/cli?action=execute"
    body="<nsxcli><command>show logical-router list all</command></nsxcli>"
    conn=requests.post(url,auth=(nsx_username,nsx_password),verify=False,headers=header,data=body)
    output=conn.text
    print "The Logical Router List"
    print "*" * 100    
    print output

list_dlr()


def list_esg():
    url="https://"+nsxmgr+"/api/1.0/nsx/cli?action=execute"
    body="<nsxcli><command>show edge all</command></nsxcli>"
    conn=requests.post(url,auth=(nsx_username,nsx_password),verify=False,headers=header,data=body)
    output=conn.text
    print "The NSX Edge List"
    print "*" * 100
    print output
    esg_id=re.findall("edge-.{1,4}",output)
    return esg_id

edge_id=list_esg()
#print edge_id

def esg_info():
    for id in edge_id:
        url="https://"+nsxmgr+"/api/4.0/edges/%s" %id
        conn=requests.get(url,auth=(nsx_username,nsx_password),verify=False)
        output=conn.text
        root=ET.fromstring(output)
	for edge in root.findall('.'):
	    eid=edge.find('id').text
	    ename=edge.find('name').text
            print "*" * 100
            print "Edge Info: %s " %ename
            print "*" * 100
            print 'ESG-ID ','|','VIC ','|','PG-Name','|','Link-Type','|','Conn_Stat','|','PG-ID','|','PG-Name'
	    for vnic in root.findall('./vnics/vnic'):
		enic=vnic.find('label').text
		evname=vnic.find('name').text
		etype=vnic.find('type').text
		eisConnected=vnic.find('isConnected').text
		try:
	            eportgroup=vnic.find('portgroupId').text
		    eportgroupname=vnic.find('portgroupName').text
		except AttributeError:
		    eportgroup="None"
		    eportgroupname="None"
		print eid,"  |",enic,'|',evname,'|',etype,'|',eisConnected,'|',eportgroup,'|',eportgroupname

esg_info()
