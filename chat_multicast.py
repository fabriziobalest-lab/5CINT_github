import socket
import struct
import threading

# ============================================================
# CONFIGURAZIONE
# ============================================================

MULTICAST_IP = "239.10.10.10"
PORTA = 5000

# ============================================================
# IP DEL PC
#
# PC A -> 172.16.7.162
# PC B -> 172.16.7.146
# ============================================================

IP_LOCALE = "172.16.7.156"


# ============================================================
# NOME UTENTE
# ============================================================

nome = input("Inserisci il tuo nome: ").strip()

if not nome:
    nome = "Anonimo"


# ============================================================
# CREAZIONE SOCKET
# ============================================================

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM,
    socket.IPPROTO_UDP
)

sock.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)


# ============================================================
# BIND DELLA PORTA
# ============================================================

try:
    sock.bind(("", PORTA))

except OSError as e:
    print(f"\nErrore: impossibile utilizzare la porta UDP {PORTA}.")
    print(e)
    sock.close()
    raise SystemExit(1)


# ============================================================
# CONFIGURAZIONE INTERFACCIA MULTICAST
# ============================================================

interfaccia = socket.inet_aton(IP_LOCALE)

# Forziamo l'invio multicast attraverso Ethernet 3
sock.setsockopt(
    socket.IPPROTO_IP,
    socket.IP_MULTICAST_IF,
    interfaccia
)


# ============================================================
# JOIN DEL GRUPPO MULTICAST
# ============================================================

gruppo = socket.inet_aton(MULTICAST_IP)

mreq = struct.pack(
    "4s4s",
    gruppo,
    interfaccia
)

try:
    sock.setsockopt(
        socket.IPPROTO_IP,
        socket.IP_ADD_MEMBERSHIP,
        mreq
    )

except OSError as e:

    print("\nErrore durante l'iscrizione al gruppo multicast:")
    print(e)

    sock.close()
    raise SystemExit(1)


# ============================================================
# FUNZIONE RICEZIONE
# ============================================================

def ricevi_messaggi():

    while True:

        try:

            dati, indirizzo = sock.recvfrom(4096)

            messaggio = dati.decode("utf-8")

            print(f"\n{messaggio}")
            print("> ", end="", flush=True)

        except OSError:
            # Socket chiuso
            break

        except UnicodeDecodeError:

            print("\nErrore: messaggio ricevuto non valido.")
            print("> ", end="", flush=True)

        except Exception as e:

            print(f"\nErrore ricezione: {e}")
            print("> ", end="", flush=True)


# ============================================================
# AVVIO THREAD RICEZIONE
# ============================================================

thread_ricezione = threading.Thread(
    target=ricevi_messaggi,
    daemon=True
)

thread_ricezione.start()


# ============================================================
# INTERFACCIA CHAT
# ============================================================

print()
print("=" * 60)
print("                 CHAT UDP MULTICAST")
print("=" * 60)
print(f"Gruppo multicast : {MULTICAST_IP}")
print(f"Porta UDP        : {PORTA}")
print(f"Interfaccia      : {IP_LOCALE}")
print(f"Nome             : {nome}")
print("=" * 60)
print()
print("Scrivi un messaggio e premi INVIO.")
print("Digita /quit per uscire.")
print()


# ============================================================
# CICLO PRINCIPALE
# ============================================================

try:

    while True:

        testo = input("> ")

        # ----------------------------------------------------
        # USCITA
        # ----------------------------------------------------

        if testo.strip().lower() == "/quit":

            print("Chiusura della chat...")
            break

        # ----------------------------------------------------
        # IGNORA MESSAGGI VUOTI
        # ----------------------------------------------------

        if not testo.strip():
            continue

        # ----------------------------------------------------
        # CREA MESSAGGIO
        # ----------------------------------------------------

        messaggio = f"[{nome}] {testo}"

        dati = messaggio.encode("utf-8")

        # ----------------------------------------------------
        # INVIA AL GRUPPO MULTICAST
        # ----------------------------------------------------

        try:

            sock.sendto(
                dati,
                (MULTICAST_IP, PORTA)
            )

        except OSError as e:

            print(f"\nErrore durante l'invio: {e}")


# ============================================================
# CTRL+C
# ============================================================

except KeyboardInterrupt:

    print("\n")
    print("Chiusura della chat...")


# ============================================================
# CHIUSURA
# ============================================================

finally:

    try:

        sock.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_DROP_MEMBERSHIP,
            mreq
        )

    except OSError:
        pass

    sock.close()

    print("Socket chiuso.")
    print("Chat terminata.")