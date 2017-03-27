/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package nlpdemo;

import java.io.FileReader;
import java.io.IOException;
import java.util.List;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.process.CoreLabelTokenFactory;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.process.PTBTokenizer;
import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.util.logging.Level;
import java.util.logging.Logger;
import static jdk.nashorn.internal.parser.TokenType.EOF;
/**
 *
 * @author nitishchandra
 */
public class NLPDemo {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws FileNotFoundException, IOException {
        BufferedReader br = new BufferedReader(new FileReader("/Users/nitishchandra/Downloads/NLP/stanfordTokenizer/stanford-postagger-full-2015-12-09/sample-input.txt"));
       MaxentTagger tagger =  new MaxentTagger("/Users/nitishchandra/Downloads/NLP/stanfordTokenizer/stanford-postagger-full-2015-12-09/models/english-left3words-distsim.tagger");
      BufferedWriter bw = new BufferedWriter(new FileWriter("/Users/nitishchandra/Downloads/NLP/stanfordTokenizer/stanford-postagger-full-2015-12-09/sample-output.txt"));
        try {
            int i=0;
            String a =null;
            String tagged = null;
            while((a=br.readLine())!=null){
                i=i+1;
     tagged = tagger.tagString(a);
           bw.write(tagged+"\n");
        //a = br.readLine();
    }
     //System.out.println(i);
            
            
        } catch (IOException ex) {
            Logger.getLogger(NLPDemo.class.getName()).log(Level.SEVERE, null, ex);
        }
        br.close();
        bw.close();
 
  // option #2: By token
   
   PTBTokenizer ptbt = new PTBTokenizer(new FileReader("sample-output.txt"),
          new CoreLabelTokenFactory(), "normalizeParentheses=false");
  for (CoreLabel label; ptbt.hasNext(); ) {
    label = (CoreLabel) ptbt.next();
    
    System.out.println(label);
  }
        // TODO code application logic here
    }
    
}
