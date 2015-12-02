import java.net.ServerSocket;
import java.net.Socket;

public class Connector {

	private static ServerSocket serverSocket;
	private static Socket clientSocket = null;
	
	public static void main(String[] args) {
		try {
			serverSocket = new ServerSocket(4444);
			System.out.println("Server started.");
		} catch (Exception e) {
			System.err.println("Port already in use.");
			System.exit(1);
		}

		while (true) {
			try {
				clientSocket = serverSocket.accept();
				//System.out.println("Accepted connection : " + clientSocket);

				new Thread(new MainServer(clientSocket)).start();

			} catch (Exception e) {
				System.err.println("Error in connection attempt.");
			}
		}

	}

}
