{
	"do_info": {
		"description": "Apache HBase", 
		"homepage":    "http://hbase.apache.org/",
		"license":     "Apache-2.0",
		"filename":    "hbase-0.94.16_openbus-r1.bd"
	},
	
	"do_download": {
		"src_uri":    "http://ftp.cixug.es/apache/hbase/hbase-0.94.16/hbase-0.94.16.tar.gz",
		"src_md5sum": "9080bf960ec0194881d6889e4be90701"
	},

	"do_fetch": {
		"download_cmd": "wget"
	},

	"do_package": {
		"commands": ["rpmbuild hadoop",
			     "rpmbuild otra cosa"]
	}
}