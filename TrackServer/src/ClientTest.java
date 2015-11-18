import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.net.Socket;

public class ClientTest {
	private static Socket sock;
	private static String fileName;
	private static BufferedReader stdin;
	private static PrintStream os;
	public static void main(String[] args) throws IOException {
		try {
			sock = new Socket("10.106.78.73", 4444);
			stdin = new BufferedReader(new InputStreamReader(System.in));
		} catch (Exception e) {
			System.err
					.println("Cannot connect to the server, try again later.");
			System.exit(1);
		}

		os = new PrintStream(sock.getOutputStream());
		os.println("IM HERE");
	}
}
