import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.ArrayList;

public class MainServer implements Runnable{
	private Socket clientSocket;
	private ArrayList<KeyVal> req = new ArrayList<>();
	public PrintWriter out;
	OutputStream os;
	String basePath = "C:\\Users\\mike.JOLLEY\\Documents\\trackers";
	public MainServer(Socket client) {
		this.clientSocket = client;
		try {
			os = this.clientSocket.getOutputStream();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	
	@Override
	public void run() {	
		try{
			out = new PrintWriter(clientSocket.getOutputStream(),true);
			BufferedReader ins = new BufferedReader(
	                new InputStreamReader(clientSocket.getInputStream()));
			String line;
			int count=0;
	        while ((line = ins.readLine()) != null) {
	        	if(count==0){
	        		System.out.println(line);
	        		String tokens[] = line.split(" ");
	        		String params[]=tokens[1].split("&");
	        		for(int i=0;i<params.length;i++){
	        			String info[]=params[i].split("=");
	        			KeyVal obj = new KeyVal(info[0],info[1]);
	        			req.add(obj);
	        		}
	        	break;		
	        	}
	        }
			
	        String command = req.get(0).val;
	        
	        if(command.equalsIgnoreCase("list")){
	    		try{
	    			File[] fileList=getList(basePath);
	    			for (int i = 1; i < fileList.length; i++) {
	    				BufferedReader in = new BufferedReader(new FileReader(fileList[i]));
	    				String str="";
	    				for(int w=0;w<4;w++){
	    					if(w!=2){
	    						String result = in.readLine().split(":")[1];
	    					      	str=str+result;
	    					}	
	    				}
	    				System.out.println(str);
	    				os.write(str.getBytes());
	    				in.close();
	    			}
	    		}
	    		catch(Exception e){
	    			System.out.println(e);
	    		
	    		}
	    	}
	    	else if(command.equalsIgnoreCase("get")){
	    	    String filename = req.get(1).val;//request.getParameter("filenametrack");
	    	    String contents = readFile(basePath+"/"+filename);
	    	    out.println(contents);
	    	}
	    	else if(command.equalsIgnoreCase("createtracker")){
	    		System.out.println("creating.....");
	    		String filename = req.get(1).val;//request.getParameter("filename");
	    		String filesize = req.get(2).val;//request.getParameter("filesize");
	    		String desc = req.get(3).val;//request.getParameter("description");
	    		String md5 = req.get(4).val;//request.getParameter("md5");
	    		String ip = req.get(5).val;//request.getParameter("ip");
	    		String port = req.get(6).val;//request.getParameter("port");
	    		String timestamp = req.get(7).val;//request.getParameter("timestamp");
	    		try{
	    			PrintWriter writer = new PrintWriter(basePath+"/"+filename, "UTF-8");
		    		writer.println("File Name: "+filename);
		    		writer.println("File Size: "+filesize);
		    		writer.println("Description: "+desc);
		    		writer.println("MD5: "+md5);
		    		writer.println(ip+":"+port+":"+"0:"+filesize+":"+timestamp);
		    		writer.close();
		    		out.println("200:Create Tracker Successful");
	    		}
	    		catch(Exception e){
	    			System.out.println(e);
	    			out.println("Create Tracker Failure");
	    		}
	    		
	    		
	    	}
	    	else if(command.equalsIgnoreCase("updatetracker")){
		    	String filename = req.get(1).val;//request.getParameter("filename");
		    	String sbyte = req.get(2).val;//request.getParameter("sbyte");
		    	String ebyte = req.get(3).val;//request.getParameter("ebyte");
		    	String ip = req.get(4).val;//request.getParameter("ip");
		    	String port = req.get(5).val;//request.getParameter("port");
		    	String file = basePath+"/"+filename;
		    	try{
		    		BufferedWriter out1 = new BufferedWriter (new FileWriter(file,true));
		    		out1.write("\n"+ip+":"+port+":"+sbyte+":"+ebyte);
		    		out1.close();
		    		os.write(("Update Tracker Successful").getBytes());
	    		}
	    		catch(Exception e){
	    			System.out.println(e);
	    		}
	    	}
	    	else{
	    		os.write(("Invalid Command").getBytes());
	    	}
		}
		catch (Exception e){
			System.out.println(e);
		}
		req.clear();
	}
	public File[] getList(String path) throws IOException{
		  File folder = new File(path);
		  File[] listOfFiles = folder.listFiles();
		  return listOfFiles;
	}
	public String readFile(String fileName) throws IOException {
	    BufferedReader br = new BufferedReader(new FileReader(fileName));
	    try {
	        StringBuilder sb = new StringBuilder();
	        String line = br.readLine();

	        while (line != null) {
	            sb.append(line);
	            sb.append("\n");
	            line = br.readLine();
	        }
	        return sb.toString();
	    } 
	    catch(Exception e){
	    	System.out.println(e);
	    	return e.toString();
	    }
	    finally {
	        br.close();
	    }
	}
}
