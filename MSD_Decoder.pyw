'''
Created on 28.05.2024

@author: efrank
'''
import tkinter as tk
from tkinter import filedialog, messagebox
import asn1tools
import os
import datetime
import webbrowser


class MSDDecoderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MSD Decoder - by MPH")
        
        current_directory = os.path.dirname(os.path.abspath(__file__))
        self.asn1_file_path = os.path.join(current_directory, "ASNs", "ESD_MSD_48.asn")
        self.asns_directory = os.path.join(current_directory, "ASNs")
        self.link_url=""

        # Configure grid layout
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=10)
        self.root.rowconfigure(2, weight=1)

        # Label 1
        self.label1 = tk.Label(root, text="MSD_ESD Hex-String", font=("Microsoft Sans Serif", 12, "bold"))
        self.label1.grid(row=0, column=0, sticky='w', padx=10, pady=10)
        
        # TextBox 1
        self.textBox1 = tk.Entry(root)
        self.textBox1.grid(row=0, column=1, sticky='we', padx=10, pady=10)
        
        # Button 1
        self.button1 = tk.Button(root, text="Decode", font=("Microsoft Sans Serif", 8, "bold"), command=self.decode)
        self.button1.grid(row=0, column=2, padx=10, pady=10)
        
        # Label 3
        self.label3 = tk.Label(root, text="MessageBox:", font=("Microsoft Sans Serif", 12, "bold"))
        self.label3.grid(row=1, column=0, sticky='w', padx=10, pady=0)
        
        # TextBox 3
        self.textBox3 = tk.Text(root, font=("Microsoft Sans Serif", 9, "bold"), wrap=tk.NONE)
        self.textBox3.grid(row=2, column=0, columnspan=3, sticky='nsew', padx=10, pady=10)
        self.textBox3.config(state=tk.NORMAL)
        
        # Scrollbar for MessageBoxp
        self.scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=self.textBox3.yview)
        self.scrollbar.grid(row=2, column=3, sticky='ns')
        self.textBox3['yscrollcommand'] = self.scrollbar.set

    def decode_hex_string(self, asn1_file_path, hex_string, main_message_type, nested_message_types):
        # Compile the ASN.1 from file
        compiler = asn1tools.compile_files(asn1_file_path, 'uper')
        
        hex_string = hex_string.rstrip('0')
    
        # Falls die Länge ungerade ist, füge eine "0" hinzu
        if len(hex_string) % 2 != 0:
            hex_string += '0'
        else:
            hex_string += '00'  # Füge "00" hinzu, wenn die Länge gerade ist, um sicherzustellen, dass es am Ende eine gerade Anzahl Zeichen bleibt

        print("hex_string =" + hex_string)
    
        # Convert HEX string to bytes
        byte_data = bytes.fromhex(hex_string)
        
        # Fill with 0x00 if length is too short
        expected_length = 1400
        if len(byte_data) < expected_length:
            byte_data += b'\x00' * (expected_length - len(byte_data))
    
        main_message = compiler.decode(main_message_type, byte_data)
        results = {main_message_type: main_message}
    
        # Dekodieren der verschachtelten Nachrichten
        for _ in range(10):
            new_nested_message_types = {}
            for field_path, message_type in nested_message_types.items():
                field_parts = field_path.split('.')
                current_message = main_message
                for part in field_parts[:-1]:
                    current_message = current_message.get(part, {})
                field = field_parts[-1]
    
                if field in current_message:
                    nested_data = current_message[field]
                    try:
                        nested_message = compiler.decode(message_type, nested_data)
                        results[message_type] = nested_message
                        main_message = nested_message
    
                        # Dekodieren weiterer verschachtelter Nachrichten, falls vorhanden
                        new_nested_message_types.update({
                            f"{field_path}.{k}": v for k, v in nested_message_types.items() if k.startswith(field_path)
                        })
                    except Exception as e:
                        print(f"Fehler beim Dekodieren {message_type}: {str(e)}")
    
            nested_message_types = new_nested_message_types
            if not nested_message_types:
                break
    
        return results
        
    
    def delete_text(self):
        self.textBox3.config(state=tk.NORMAL)
        self.textBox3.delete(1.0, tk.END)
        self.textBox3.config(state=tk.DISABLED)
        
    def print_flat_dict(self, data, i, currentLat=0.0, currentLong=0.0,posDeltaN = {"Lat": [0], "Long": [0]}, googleurl = "https://www.google.de/maps/dir/"):
        vin_parts = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    i, currentLat, currentLong, posDeltaN,googleurl = self.print_flat_dict(value, i, currentLat, currentLong,posDeltaN, googleurl)
                elif isinstance(value, list):
                    for index, item in enumerate(value):
                        i, currentLat, currentLong, posDeltaN, googleurl = self.print_flat_dict(item, i, currentLat, currentLong,posDeltaN, googleurl)
                else:
                    try:
                        if ( abs(float(value)) == 255):
                            self.printErrors(f"{key}: hardly plausible ({value})")
                            continue
                    except:
                        pass
                    if key in ['positionLatitude', 'positionLongitude']:
                        try:
                            if key == 'positionLatitude':
                                print("positionLatitude (mArcSec) = " + str(value) )
                                
                            if key == 'positionLongitude':
                                print("positionLongitude (mArcSec) = " + str(value))
                                
                            value = float(value) / 3600000 #in Grad umgerechnet
                            if key == 'positionLatitude':
                                lat = value
                                currentLat = value
                                posDeltaN["Lat"][0] = currentLat;
                                if(currentLat > 90):
                                    self.printErrors(f"{key}: hardly plausible ({posDeltaN['Lat'][0]})")
                                    continue
                                self.show_message(f"{key}: {posDeltaN['Lat'][0]}")
                                googleurl = googleurl + str(posDeltaN["Lat"][0])+","
                            if key == 'positionLongitude':
                                currentLong = value
                                posDeltaN["Long"][0] = currentLong;
                                lon = value
                                if(currentLong > 180):
                                    self.printErrors(f"{key}: hardly plausible ({posDeltaN['Long'][0]})")
                                    continue
                                self.show_message(f"{key}: {posDeltaN['Long'][0]}")
                                googleurl = googleurl + str(posDeltaN["Long"][0])+"/"
                        except ValueError:
                            self.show_message(f"{key}: {value} (cannot convert to float)")
                    elif key in ['callbackNumber1', 'callbackNumber2']:
                        try:
                            if isinstance(value, bytes):
                                value = value.hex()
                            self.show_message(f"{key}: {value}")
                        except Exception as e:
                            self.show_message(f"{key}: {value} (cannot process, error: {str(e)})")
                    else:
                        if key == 'timestamp':
                            if(value == 0):
                                self.printErrors(f"{key}: hardly plausible ({value})")
                                continue
                            if(value != 0):
                                try:
                                    value = datetime.datetime.utcfromtimestamp(int(value))
                                
                                except:
                                    print("Datum konnte nicht umgewandelt werden")
                        if key == 'latitudeDelta':
                            if currentLat is not None:
                                try:
                                    print("Lat: ArcSec Value("+ str(i) +")RAW = " + str(value))
                                    #if (i <= 2):
                                    delta_arcSec = ((float(value)))*100
                                    #if (i > 2):
                                        #delta_arcSec = ((float(value)))
                                    print("Lat: Delta_ArcSec("+ str(i) +") (Edgar) = " + str(delta_arcSec))
                                    delta_deg = delta_arcSec / 3600000.0
                                    latN = currentLat - delta_deg
                                    posDeltaN["Lat"][i] = posDeltaN["Lat"][i-1] + delta_deg;
                                    
                                    if(latN > 90):
                                        self.printErrors(f"{key}: hardly plausible ({latN})")
                                        googleurl = googleurl + str(posDeltaN["Lat"][i])+","
                                        continue
                                    self.show_message(f"latitudeDeltaN{i}: {latN}")
                                    #if (i <= 2):
                                    googleurl = googleurl + str(posDeltaN["Lat"][i])+","
                                except ValueError:
                                    self.show_message(f"{key}: {posDeltaN['Lat'][i]} (cannot convert to float)")
                                    
                        elif key == 'longitudeDelta':
                            if currentLong is not None:
                                try:
                                    print("Long: ArcSec Value("+ str(i) +")RAW = " + str(value))
                                    #if (i <= 2) :
                                    delta_arcSec = ((float(value)))*100
                                    #if (i>2):
                                        #delta_arcSec = ((float(value)))
                                    print("Long: Delta_ArcSec("+ str(i) +") (Edgar) = " + str(delta_arcSec))
                                    delta_deg = delta_arcSec / 3600000.0
                                    longN = currentLong - delta_deg
                                    posDeltaN["Long"][i] = posDeltaN["Long"][i-1] + delta_deg;
                                    
                                    if(currentLong > 180):
                                        self.printErrors(f"{key}: hardly plausible ({longN})")
                                        googleurl = googleurl + str(posDeltaN["Long"][i])+"/"
                                        i += 1
                                        continue
                                    #if (i <= 2):
                                    googleurl = googleurl + str(posDeltaN["Long"][i])+"/"
                                    
                                    self.show_message(f"longitudeDeltaN{i}: {posDeltaN['Long'][i]}")
                                    i += 1
                                except ValueError:
                                    self.show_message(f"{key}: {posDeltaN['Long'][i]} (cannot convert to float)")
                        else:
                            self.show_message(f"{key}: {value}")
                        
                        if 'iso' in key:
                            vin_parts.append(str(value))
    
        if vin_parts:
            vin = "VIN: " + ''.join(vin_parts)
            self.show_message(vin)
    
        return i, currentLat, currentLong, posDeltaN, googleurl
                    
    def decode(self):
        asn1_file_path = self.asn1_file_path
        hex_data = self.textBox1.get()
        hex_data = hex_data.replace(" ", "")
        self.delete_text()
        
        # Main Message Type und Nested Messages
        main_message_type = 'ECallMessage'
        nested_message_types = {
            'msd': 'MSDMessage',
            'optionalAdditionalData.data': 'ESDMessage'
        }
    
        # Extrahiere die OID und dekodiere die Nachricht
        decoded_oid = self.decode_hex_string(asn1_file_path, hex_data, main_message_type, nested_message_types)
        oid = None
    
        if 'MSDMessage' in decoded_oid:
            try:
                full_oid = decoded_oid['MSDMessage']['optionalAdditionalData']['oid']
                oid = full_oid.split(".")[-1]
                print("Die OID ist: " + oid)
            except KeyError:
                # Falls keine OID gefunden wird, nehme MSD.asn
                self.show_message("Keine OID gefunden, verwende MSD.asn.")
                asn1_file_path = os.path.join(self.asns_directory, "ESD_MSD_49.asn")
        else:
            self.show_message("Nur MSD Nachricht gefunden, verwende MSD.asn.")
            asn1_file_path = os.path.join(self.asns_directory, "ESD_MSD_49.asn")
    
        # Finde die passende ASN-Datei oder benutze MSD.asn
        if oid:
            try:
                asn1_file_path = self.find_matching_asn_file(oid)
            except Exception as e:
                self.show_message(f"Keine Datei für die OID {oid} gefunden! Verwende MSD.asn. Error: {str(e)}")
                asn1_file_path = os.path.join(self.asns_directory, "ESD_MSD_49.asn")
    
        # Dekodiere den Hex-String erneut mit der richtigen ASN-Datei
        decoded_messages = self.decode_hex_string(asn1_file_path, hex_data, main_message_type, nested_message_types)
        print(decoded_messages)
    
        # Ausgabe der dekodierten Daten
        i = 1
        currentLat = 0.0
        currentLong = 0.0
        googleurl = "https://www.google.de/maps/dir/"
        posDeltaN = {"Lat": [None]*10, "Long":[None]*10}
        
        for message_type, message in decoded_messages.items():
            self.show_message(f"{message_type}:")
            i, currentLat, currentLong, posDeltaN, googleurl = self.print_flat_dict(message, i, currentLat, currentLong, posDeltaN, googleurl)
            self.show_message("")
    
        self.link_url = googleurl
        self.show_message("Google Maps Link: " + googleurl, is_link=True)

    def find_matching_asn_file(self, oid):
        for filename in os.listdir(self.asns_directory):
            if oid in filename:
                self.show_message(f"Zugehörige ASN Datei gefunden: {filename}")
                return os.path.join(self.asns_directory, filename)
        
        self.show_message("Keine Zugehörige ASN Datei gefunden. Verwende ESD_MSD_49.asn")
        return os.path.join(self.asns_directory, "ESD_MSD_49.asn")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("ASN files", "*.asn")])
        if file_path:
            self.textBox2.delete(0, tk.END)
            self.textBox2.insert(0, file_path)
            self.show_message(f"ASN Datei ausgewählt: {file_path}")

    def show_message(self, message, is_link=False):
        self.textBox3.config(state=tk.NORMAL)
        if is_link:
            self.textBox3.insert(tk.END, message)
            self.textBox3.tag_add("link", "end-1c linestart", "end-1c lineend")
            self.textBox3.tag_config("link", foreground="blue", underline=1)
            self.textBox3.tag_bind("link", "<Button-1>", lambda event: webbrowser.open_new(self.link_url))
        else:
            self.textBox3.insert(tk.END, message + "\n")
        self.textBox3.config(state=tk.DISABLED)
    
    def printErrors(self, message):
        self.textBox3.config(state=tk.NORMAL)
        self.textBox3.insert(tk.END, message + "\n", 'error')
        self.textBox3.tag_configure('error', foreground='red')
        self.textBox3.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x450")
    app = MSDDecoderApp(root)
    root.mainloop()