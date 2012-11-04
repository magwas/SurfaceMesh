<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="2.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<!-- removes properties
e.g.
saxon9 -xsl:../rmprop.xslt namere="^Force" -s:Document.old.xml -o:Document.xml
removes all praperties whose name starts with "Force"
-->
	<xsl:param name="namere"/>
	<xsl:output method="xml" version="1.0" encoding="utf-8" indent="no" omit-xml-declaration="no"/>

	<xsl:template match="Property">
		<xsl:if test="not(matches(@name,$namere))">
    	<xsl:copy>
     	 <xsl:apply-templates select="*|@*|text()|processing-instruction()|comment()"/>
    	</xsl:copy>
		</xsl:if>
	</xsl:template>

	<xsl:template match="Properties">
		<xsl:variable name="props">
      <xsl:apply-templates select="*|text()|processing-instruction()|comment()"/>
		</xsl:variable>
		<Properties>
			<xsl:attribute name="Count" select="count($props//Property)"/>
			<xsl:copy-of select="$props"/>
		</Properties>
	</xsl:template>

  <xsl:template match="@*|*|processing-instruction()|comment()">
    <xsl:copy>
      <xsl:apply-templates select="*|@*|text()|processing-instruction()|comment()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>

