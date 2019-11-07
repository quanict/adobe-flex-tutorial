Messaging
=========

To this point, the article has focused on creating applications that use a call-response model 
to make asynchronous calls to Java classes on the server.
Using BlazeDS or LiveCycle Data Services, you can also build applications that use a publish-subscribe model 
to send messages between multiple Flex clients (through the server), push messages from the server to clients,
and/or send messages to other JMS enabled messaging clients.
A Flex application can `send messages to a destination <http://help.adobe.com/en_US/LiveCycleDataServicesES/3.1/Developing/WSc3ff6d0ea77859461172e0811f00f6e70f-8000Update.html>`__ on the server
and any other clients subscribed to that same destination will receive those messages.

A simple application using messaging is instant messaging where text is exchanged between clients.
Messaging can also be used to create rich collaborative data applications where data changes made in one client are "instantly" seen by other clients viewing the same data. Server sending notifications to clients, clients receiving sport score updates, auction sites having access to real-time bids, applications for trading stocks, foreign exchange etc. are all examples of applications that can be developed using the messaging infrastructure.

Defining destinations
---------------------

Similar to how you configure remoting, you configure messaging by defining destinations in a server-side configuration file, in this case, messaging-config.xml. A messaging destination can be as simple as this:

.. code :: xml

    <destination id="chat">

in which case it uses the default adapter and channel defined in the messaging-config.xml file:

.. code :: xml

    <adapters>
        <adapter-definition id="actionscript" class="flex.messaging.services.messaging.adapters.ActionScriptAdapter" default="true" />
        <adapter-definition id="jms" class="flex.messaging.services.messaging.adapters.JMSAdapter"/>
    </adapters>
    <default-channels>
        <channel ref="my-rtmp"/>
        <channel ref="my-streaming-amf"/>
    </default-channels>

The first adapter defined, actionscript, is the default adapter and is used to exchange messages between Flex clients. The jms adapter can be used instead to bridge to JMS destinations. The default channel is my-rtmp, a real-time streaming channel with failover to a streaming AMF channel (both defined in the services-config.xml file). Channels are discussed in more detail in the next section, Selecting a channel.

You can also specify additional properties when defining a destination, including network and server properties. In the following destination, the chat destination is configured to use the my-polling-amf channel, users are never unsubscribed even with no activity, messages are kept on the server indefinitely until there are 1000 messages at which time the oldest is replaced, and only clients that have been authenticated and authorized against the trusted security constraint defined in the services-config.xml file (see the Security section) can publish or receive messages.

.. code :: xml

    <destination id="chat">
        <properties>
            <channels>
                <channel ref="my-polling-amf"/>
            </channels>
            <network>
                <session-timeout>0</session-timeout>
            </network>
            <server>
                <max-cache-size>1000</max-cache-size>
                <message-time-to-live>0</message-time-to-live>
                <durable>false</durable>
                <send-security-constraint ref="trusted"/>
                <subscribe-security-constraint ref="trusted"/>
            </server>
        </properties>
    </destination>