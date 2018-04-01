using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Text;

namespace multicast_client
{
    class Program
    {
        // send response by tcp
        public static void sendTcp()//object server, object message)
        {
            try
            {
                // Create a TcpClient.
                // Note, for this client to work you need to have a TcpServer 
                // connected to the same address as specified by the server, port
                // combination.
                Int32 port = 13000;
                TcpClient client = new TcpClient("127.0.0.1", port);

                // Translate the passed message into ASCII and store it as a Byte array.
                Byte[] data = System.Text.Encoding.ASCII.GetBytes("hello");

                // Get a client stream for reading and writing.
                //  Stream stream = client.GetStream();

                NetworkStream stream = client.GetStream();

                // Send the message to the connected TcpServer. 
                stream.Write(data, 0, data.Length);

                Console.WriteLine("Sent: {0}", "hello");

                // Close everything.
                stream.Close();
                client.Close();
            }
            catch (ArgumentNullException e)
            {
                Console.WriteLine("ArgumentNullException: {0}", e);
            }
            catch (SocketException e)
            {
                Console.WriteLine("SocketException: {0}", e);
            }

            Console.WriteLine("\n Press Enter to continue...");
            Console.Read();
        }

        public static void multicastListen()
        {
            Console.WriteLine("Child thread starts");
            // multicast receive:
            UdpClient client = new UdpClient();

            client.ExclusiveAddressUse = false;
            IPEndPoint localEp = new IPEndPoint(IPAddress.Any, 10000);

            client.Client.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, true);
            client.ExclusiveAddressUse = false;

            client.Client.Bind(localEp);

            IPAddress multicastaddress = IPAddress.Parse("224.3.29.71");
            client.JoinMulticastGroup(multicastaddress);

            Console.WriteLine("Listening this will never quit so you will need to ctrl-c it");

            while (true)
            {
                Byte[] data = client.Receive(ref localEp);
                string strData = Encoding.UTF8.GetString(data);
                Console.WriteLine(strData);
            }
        }
        
        static void Main(string[] args)
        {
            bool ischange = false;
            object serverIP = "";
            object snapshot = "";
            // main thread built: -- here the game will run
            Thread th = Thread.CurrentThread;
            th.Name = "MainThread";
            Console.WriteLine("This is {0}", th.Name);
            Console.ReadKey();

            // child (recieve) thread built - all the time
            Console.WriteLine("In Main: Creating the recieve thread");
            Thread recieveThread = new Thread(new ThreadStart(multicastListen));
            recieveThread.Start();
            Console.ReadKey();

            for (int i = 0; i < 50; i++)//simulates the running game
            {
                Console.WriteLine("game running");
                Thread.Sleep(1);
            }

            if (ischange)
            {
                // child (send) thread built -- enter only when want to send
                Console.WriteLine("In Main: Creating the send thread");
                Thread sendThread = new Thread(new ThreadStart(sendTcp));
                sendThread.Start();
                Console.ReadKey();
            }

        }
    }
}
