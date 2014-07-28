import os

def get_mean_sd(filename):
	"""example output format is mean:192.054843420412	stdev:59.5257431414947"""
	ifp = open(filename)
	items = ifp.readline().rstrip().split()
	ifp.close()
	return str(int(float(items[0].split(':')[1]))), str(int(float(items[1].split(':')[1]))) 

bam_path = "/home/dehms/shared/mayo/rawdata"
cutoff = 2000
ifp = open("sample_list.txt")
while ifp:
	normal = ifp.readline().rstrip()
	if not normal:
		break
	tumor = ifp.readline().rstrip()

	print "samtools view "+bam_path+normal+".AR.bam|tail -n+10000|pairend_distro.pl -rl 101 -X 4 -N 10000 -o "+normal+".pe.histo >temp"
	os.system("samtools view "+bam_path+normal+".AR.bam|tail -n+10000|pairend_distro.pl -rl 101 -X 4 -N 10000 -o "+normal+".pe.histo >temp")

	mean_normal, std_normal = get_mean_sd("temp")
	print "mean:"+mean_normal+'\t'+"std:"+std_normal

	print "samtools view "+bam_path+tumor+".AR.bam|tail -n+10000|pairend_distro.pl -rl 101 -X 4 -N 10000 -o "+tumor+".pe.histo >temp"
	os.system("samtools view "+bam_path+tumor+".AR.bam|tail -n+10000|pairend_distro.pl -rl 101 -X 4 -N 10000 -o "+tumor+".pe.histo >temp")

	mean_tumor, std_tumor = get_mean_sd("temp")
	print "mean:"+mean_normal+'\t'+"std:"+std_normal

	print "lumpy -e -mw 4 -tt 0.0 -pe bam_file:"+bam_path+normal+".AR.bam,histo_file:"+normal+".pe.histo,mean:"+mean_normal+",stdev:"+std_normal+",read_length:101,min_non_overlap:101,discordant_z:4,back_distance:20,weight:1,id:1,min_mapping_threshold:1 -pe bam_file:"+bam_path+tumor+".AR.bam,histo_file:"+tumor+".pe.histo,mean:"+mean_tumor+",stdev:"+std_tumor+",read_length:101,min_non_overlap:101,discordant_z:4,back_distance:20,weight:1,id:2,min_mapping_threshold:1 >"+normal+"_v_"+tumor+".pe.bedpe"
	os.system("lumpy -e -mw 4 -tt 0.0 -pe bam_file:"+bam_path+normal+".AR.bam,histo_file:"+normal+".pe.histo,mean:"+mean_normal+",stdev:"+std_normal+",read_length:101,min_non_overlap:101,discordant_z:4,back_distance:20,weight:1,id:1,min_mapping_threshold:1 -pe bam_file:"+bam_path+tumor+".AR.bam,histo_file:"+tumor+".pe.histo,mean:"+mean_tumor+",stdev:"+std_tumor+",read_length:101,min_non_overlap:101,discordant_z:4,back_distance:20,weight:1,id:2,min_mapping_threshold:1 >"+normal+"_v_"+tumor+".pe.bedpe")
	summary = {}
	ifp2 = open(normal+"_v_"+tumor+".pe.bedpe")
	ofp = open(normal+"_v_"+tumor+".pe.bed",'w')
	ofp2 = open(normal+"_v_"+tumor+".pe.summary.txt",'w')
	for line in ifp2:
		if line[0] == '\t':
			continue
		else:
			items = line.rstrip().split()
			label = items[10]
			try:
				summary[items[10]] += 1
			except KeyError:
				summary[items[10]] = 1
			if items[10] == 'TYPE:DELETION':
				size = int(items[5])-int(items[2])
				if size > cutoff:
					try:
						summary['TYPE:DELETION>2kb'] += 1
					except KeyError:
						summary['TYPE:DELETION>2kb'] = 1
					label = 'TYPE:DELETION>2kb'
			print >> ofp, line.rstrip()+'\t'+label
	for each in sorted(summary.keys()):
		print >> ofp2, each+'\t'+str(summary[each])
	ifp2.close()
	ofp.close()
	ofp2.close()

os.remove("temp")
os.system("rm *.histo")
ifp.close()
