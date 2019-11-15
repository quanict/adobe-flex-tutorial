Messaging
=========

.. toctree::
   :maxdepth: 0
   :caption: java_architecture

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

.. code:: xml

    <destination id="chat">

in which case it uses the default adapter and channel defined in the messaging-config.xml file:

.. code:: xml

    <adapters>
        <adapter-definition id="actionscript" class="flex.messaging.services.messaging.adapters.ActionScriptAdapter" default="true" />
        <adapter-definition id="jms" class="flex.messaging.services.messaging.adapters.JMSAdapter"/>
    </adapters>
    <default-channels>
        <channel ref="my-rtmp"/>
        <channel ref="my-streaming-amf"/>
    </default-channels>

The first adapter defined, actionscript, is the default adapter and is used to exchange messages between Flex clients. The jms adapter can be used instead to bridge to JMS destinations. The default channel is my-rtmp, a real-time streaming channel with failover to a streaming AMF channel (both defined in the services-config.xml file). Channels are discussed in more detail in the next section, Selecting a channel.

You can also specify additional properties when defining a destination,
including network and server properties.
In the following destination,
the chat destination is configured to use the **my-polling-amf** channel,
users are never unsubscribed even with no activity,
messages are kept on the server indefinitely until there are 1000 messages at which time the oldest is replaced,
and only clients that have been authenticated and authorized against the trusted security constraint defined in the `services-config.xml` file
(see the `Security section <https://www.adobe.com/devnet/flex/articles/flex_java_architecture.html#articlecontentAdobe_numberedheader_1>`__) can publish or receive messages.

.. code:: xml

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

Selecting a channel
-------------------

When defining a destination, you specify the channel to be used for the communication between the client and server including the protocol, the port, and the endpoint. Channels are defined in the services-config.xml file. For remoting, you usually use the my-amf or my-secure-amf channel. For messaging, there is larger number of channels to select from, including those that use polling or streaming, servlets or sockets, and HTTP or RTMP.

Polling channels support polling the server on some interval or on some event. The **my-polling-amf** channel polls the server every 8 seconds for new messages.

.. code:: xml

    <channel-definition id="my-polling-amf" class="mx.messaging.channels.AMFChannel">
        <endpoint url="http://{server.name}:{server.port}/{context.root}/messagebroker/amfpolling" class="flex.messaging.endpoints.AMFEndpoint"/>
        <properties>
            <polling-enabled>true</polling-enabled>
            <polling-interval-seconds>8</polling-interval-seconds>
        </properties>
    </channel-definition>

To more closely mimic a real-time connection, you can use long polling. The **my-amf-longpoll** channel is configured for long polling.

.. code:: xml

    <channel-definition id="my-amf-longpoll" class="mx.messaging.channels.AMFChannel">
        <endpoint url="http://{server.name}:{server.port}/{context.root}/messagebroker/myamflongpoll" class="flex.messaging.endpoints.AMFEndpoint"/>
        <properties>
            <polling-enabled>true</polling-enabled>
            <polling-interval-seconds>0</polling-interval-seconds>
            <wait-interval-seconds>60</wait-interval-seconds>
            <client-wait-interval-seconds>3</client-wait-interval-seconds>
            <max-waiting-poll-requests>100</max-waiting-poll-requests >
        </properties>
    </channel-definition>

When this channel is used, the client polls the server; the server poll response thread waits 60 seconds for new messages to arrive if there are no new messages on the server and then returns to the client; after receiving the poll response, the client polls again after 3 seconds; the process is repeated. The server is set to allow 100 simultaneous server poll response threads in a wait state; if exceeded, the server does not wait for new messages before returning a response. Typical application servers might have around 200 HTTP request threads available, so you need to make sure you set the maximum allowable number of polling threads to a smaller number and still leave enough threads to handle other HTTP requests.

With servers and proxy servers that support HTTP 1.1, an HTTP streaming channel can be used. A persistent connection is established between the client and the server over which server messages are pushed to the client. HTTP connections can't handle traffic in both directions, so separate, short-lived threads must be used for any other server requests. Network latency is minimized compared to long-polling because connections don’t have to be continually closed and reopened.

.. code:: xml

    <channel-definition id="my-streaming-amf" class="mx.messaging.channels.StreamingAMFChannel">
        <endpoint url="http://{server.name}:{server.port}/{context.root}/messagebroker/streamingamf" class="flex.messaging.endpoints.StreamingAMFEndpoint"/>
    </channel-definition>

Using HTTP long-polling and streaming the number of simultaneous users that can be connected to a destination is limited by the available number of server HTTP threads. For applications that will have larger numbers of simultaneous users, messages can be pushed using sockets instead of HTTP threads. LiveCycle Data Services includes a NIO-based socket server and has additional channels available for messaging that are not available with BlazeDS. These channels, defined in the services-config.xml file, all contain "nio" in their names. NIO stands for Java New Input/Output and is a collection of Java APIs for I/O operations.

If you are using LiveCycle Data Services you should use the NIO channels over the servlet based channels because they scale better,
handling thousands of simultaneous users instead of around a hundred.
There are NIO equivalents for each of the AMF polling, long polling,
and streaming channels just discussed (**my-nio-amf-poll**, **my-nio-amf-longpoll**, **my-nioamf-stream**).
These channels are still using HTTP so in the latter two cases, separate threads are still required for client-server requests and the persistent (or waiting) threads used for the server-to-client updates.

.. code:: xml

    <channel-definition id="my-nio-amf-longpoll" class="mx.messaging.channels.AMFChannel">
        <endpoint url="http://{server.name}:2080/nioamflongpoll" class="flex.messaging.endpoints.NIOAMFEndpoint"/>
        <server ref="my-nio-server"/>
        <properties>
            <polling-enabled>true</polling-enabled>
            <polling-interval-millis>0</polling-interval-millis>
            <wait-interval-millis>-1</wait-interval-millis>
        </properties>
    </channel-definition>

With LiveCycle Data Services you can choose channels that use the RTMP protocol instead of HTTP.

.. code:: xml

    <channel-definition id="my-rtmp" class="mx.messaging.channels.RTMPChannel">
        <endpoint url="rtmp://{server.name}:2037" class="flex.messaging.endpoints.RTMPEndpoint"/>
        <properties>
            <idle-timeout-minutes>20</idle-timeout-minutes>
        </properties>
    </channel-definition>

RTMP, the Real-Time Messaging Protocol, was developed by Adobe for high-performance transmission of audio, video, and data between Adobe Flash Platform technologies (like Adobe Flash Player and Adobe AIR) and is now available as an open specification. RTMP provides a full duplex socket connection so that a single connection can be used for all communication between the client and the server, including all RPC and messaging. Another benefit of RTMP is that when a client connection is closed, the endpoint is immediately notified (so the application can instantly respond) unlike when using the HTTP protocol where endpoints do not receive notification until the HTTP session on the server times out. Because RTMP generally uses a non-standard port, though, it is often blocked by client firewalls. In this case, the channel automatically attempts to tunnel over HTTP.

As a general recommendation, if you are using LiveCycle Data Services, use RTMP with failover to NIO-based long-polling. If using BlazeDS, use AMF long-polling or AMF streaming with failover to long-polling.

Sending and receiving messages
------------------------------

To send messages from a Flex application you use the Producer API and to receive messages, the Consumer API. A basic application sends, receives, and displays messages is shown here.

.. code:: xml

    <s:Application xmlns:fx="http://ns.adobe.com/mxml/2009"
        xmlns:s="library://ns.adobe.com/flex/spark"
        xmlns:mx="library://ns.adobe.com/flex/mx"
        creationComplete="application1_creationCompleteHandler()">
        <fx:Script>
        <![CDATA[
            import mx.messaging.events.MessageEvent;
            import mx.messaging.messages.AsyncMessage;
            protected function application1_creationCompleteHandler():void{
                consumer.subscribe();
            }
            protected function button1_clickHandler(event:MouseEvent):void{
            var message:AsyncMessage=new AsyncMessage();
            message.headers.username=username.text;
            message.body=msg.text;
            producer.send(message);
            msg.text="";
            }
            protected function consumer_messageHandler(event:MessageEvent):void{
            messageDisplay.text+=event.message.headers.username+": "+event.message.body+"\n";
            }
        ]]>
        </fx:Script>
        <fx:Declarations>
            <s:Producer id="producer" destination="chat"/>
            <s:Consumer id="consumer" destination="chat" message="consumer_messageHandler(event)"/>
        </fx:Declarations>
        <s:TextArea id="messageDisplay" width="400"/>
        <s:TextInput id="username" x="0" y="160"/>
        <s:TextInput id="msg" x="136" y="160"/>
        <s:Button label="Send" click="button1_clickHandler(event)" x="272" y="160"/>
    </s:Application>

For more information about using the messaging service, see the BlazeDS and LCDS documentation.


