/* vim:set ts=4:sw=4:et:sts=4:ai:tw=80
 *
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import org.apache.log4j.*
import groovy.util.logging.*
import java.security.MessageDigest

/**
 * Class for download the source files
 *
 * This class implements methods for HTTP, FTP,
 * GIT, SVN source code downloads.
 *
 * @author Javi Roman <javiroman@kernel-labs.org>
 *
 */
class FileDownloader {
	def BDROOT
	def LOG
	def globalConfig

	def FileDownloader(l, r, g) {
		LOG = l
		BDROOT = r
		globalConfig = g
        LOG.info "[FileDownloader] constructor, checking enviroment"
	}

	def getMD5sum(file, len) {
		File f = new File(file)
		if (!f.exists() || !f.isFile()) {
				println "Invalid file $f provided"
				println "Usage: groovy sha1.groovy <file_to_hash>"
		}

		def messageDigest = MessageDigest.getInstance("MD5")

		//long start = System.currentTimeMillis()

		f.eachByte(len) { byte[] buf, int bytesRead ->
				messageDigest.update(buf, 0, bytesRead);
		}

		def sha1Hex = new BigInteger(1, messageDigest.digest()).toString(16)

		//long delta = System.currentTimeMillis()-start

		println "$sha1Hex $file"
	}

	def downloadFromURL(address) {
		def contentLength

		strUrl = address
		url = new URL(strUrl)
		connection = url.openConnection()
		connection.connect()

		// Check if the request is handled successfully  
		if(connection.getResponseCode() / 100 == 2) {
				// size of the file to download (in bytes)  
				contentLength = connection.getContentLength()
		}

		println "Downloading " + address.split("/")[-1] +
				" ($contentLength bytes)"

		def file = new FileOutputStream(address.tokenize("/")[-1])
		def out = new BufferedOutputStream(file)
		out << new URL(address).openStream()
		out.close()

		return contentLength
	}
}