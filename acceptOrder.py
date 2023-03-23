#accept order
#dapet dari driver UI, kirim request ke order management buat update status, receive reponse 
#dari order management jadi 'picked up', 
#kirim request ke driver microservice update driver status, receive response from driver microservice,
#fire back to retoran UI


#finish delivery
#dapet request dari driver UI, kirim request ke order management buat update status order jadi 'delivered'
#update driver availability jadi 'availabile' lagi